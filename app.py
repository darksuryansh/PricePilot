import subprocess
import json
import re
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
import pymongo
from datetime import datetime, timedelta
from bson import ObjectId
import google.generativeai as genai
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
# Enable CORS for React frontend - allow all common dev ports
CORS(app, origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:5173", "http://127.0.0.1:5174"], supports_credentials=True)

# MongoDB connection
client = pymongo.MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client['price_tracker_db']
products_collection = db['products']
price_history_collection = db['price_history']
reviews_collection = db['reviews']
users_collection = db['users']

# Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# Helper function to parse rating string to float
def parse_rating(rating_str):
    """Parse rating from string like '4.2 out of 5 stars' to float"""
    if not rating_str:
        return 0.0
    try:
        # Extract first number from string
        import re
        match = re.search(r'(\d+\.?\d*)', str(rating_str))
        if match:
            return float(match.group(1))
    except:
        pass
    return 0.0

# Helper function to parse reviews count
def parse_reviews_count(reviews_str):
    """Parse reviews count from string like '34,021 ratings' to int"""
    if not reviews_str:
        return 0
    try:
        # Remove commas and extract numbers
        import re
        cleaned = re.sub(r'[,\s]', '', str(reviews_str))
        match = re.search(r'(\d+)', cleaned)
        if match:
            return int(match.group(1))
    except:
        pass
    return 0

# Helper function to parse price string to numeric
def parse_price(price_str):
    """Parse price from string like '₹1,599.00' to float"""
    if not price_str:
        return 0.0
    try:
        # Remove currency symbols, commas, and spaces
        import re
        cleaned = re.sub(r'[₹,\s]', '', str(price_str))
        match = re.search(r'(\d+\.?\d*)', cleaned)
        if match:
            return float(match.group(1))
    except:
        pass
    return 0.0

# Helper function to extract product ID from URL
def extract_product_id(url):
    """Extract ASIN or product ID from URL"""
    # Amazon ASIN pattern
    amazon_match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if amazon_match:
        return amazon_match.group(1), 'amazon'
    
    # Flipkart PID pattern
    flipkart_match = re.search(r'pid=([A-Z0-9]+)', url)
    if flipkart_match:
        return flipkart_match.group(1), 'flipkart'
    
    # Myntra product ID pattern
    myntra_match = re.search(r'/(\d{6,})/buy', url)
    if myntra_match:
        return myntra_match.group(1), 'myntra'
    
    return None, None

# API route to scrape a product
@app.route('/api/scrape', methods=['POST'])
def scrape():
    """Scrape product data from URL"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Determine which spider to use
    spider_name = ''
    if 'amazon.in' in url:
        spider_name = 'amazon'
    elif 'myntra.com' in url:
        spider_name = 'myntra'
    elif 'flipkart.com' in url:
        spider_name = 'flipkart'
    elif 'meesho.com' in url:
        spider_name = 'meesho'
    else:
        return jsonify({'error': 'Unsupported website. Please use Amazon, Flipkart, or Myntra URLs'}), 400

    # Extract product ID to check if already exists
    product_id, platform = extract_product_id(url)
    
    # Scrapy project path
    scrapy_project_path = os.path.join(os.path.dirname(__file__), 'price_scraper')
    
    # Construct the Scrapy command as a string for Windows shell
    # Use double quotes to properly escape the URL
    command_str = f'conda run -n webdev scrapy crawl {spider_name} -a "url={url}"'

    try:
        # Run the Scrapy command
        print(f"Running command: {command_str}")
        print(f"Working directory: {scrapy_project_path}")
        
        result = subprocess.run(
            command_str, 
            check=False,  # Don't raise exception on non-zero exit code
            cwd=scrapy_project_path, 
            shell=True,
            capture_output=True,
            text=True,
            timeout=200  # 3 minute timeout
        )
        
        print(f"Scraping process completed with return code: {result.returncode}")
        print(f"stdout: {result.stdout[-1000:] if result.stdout else 'None'}")
        print(f"stderr: {result.stderr[-1000:] if result.stderr else 'None'}")
        
        # Check if scraping was successful by looking for success indicators in output
        success_indicators = [
            'Spider closed (finished)',
            'item_scraped_count',
            'Stored/Updated product'
        ]
        
        output_text = (result.stdout or '') + (result.stderr or '')
        scraping_succeeded = any(indicator in output_text for indicator in success_indicators)
        
        if scraping_succeeded:
            print(f"✓ Scraping completed successfully")
            
            # After scraping, search for similar products on other platforms
            # Get the scraped product from database
            if platform == 'amazon':
                main_product = products_collection.find_one({'asin': product_id})
            else:
                main_product = products_collection.find_one({'product_id': product_id})
            
            cross_platform_results = []
            
            if main_product:
                # Extract search terms from the scraped product
                title = main_product.get('title', '')
                brand = main_product.get('brand', '')
                
                # Create search query from brand and title
                search_words = []
                if brand:
                    search_words.append(brand)
                if title:
                    # Take first few significant words from title
                    title_words = title.split()[:5]
                    search_words.extend(title_words)
                
                print(f"🔍 Searching for similar products with keywords: {' '.join(search_words)}")
                
                # Search across all platforms except the source platform
                other_platforms = ['amazon', 'flipkart', 'myntra', 'meesho']
                if platform in other_platforms:
                    other_platforms.remove(platform)
                
                for other_platform in other_platforms:
                    # Build regex search for each platform
                    search_conditions = []
                    for word in search_words[:4]:  # Use first 4 words
                        if len(word) > 3:  # Only meaningful words
                            search_conditions.append({
                                '$or': [
                                    {'title': {'$regex': word, '$options': 'i'}},
                                    {'brand': {'$regex': word, '$options': 'i'}}
                                ]
                            })
                    
                    if search_conditions:
                        # Add platform filter
                        platform_filter = {'platform': other_platform}
                        
                        matching_products = list(products_collection.find({
                            '$and': search_conditions + [platform_filter]
                        }).limit(1))
                        
                        if matching_products:
                            match = matching_products[0]
                            match_id = match.get('asin') or match.get('product_id')
                            cross_platform_results.append({
                                'platform': other_platform,
                                'product_id': match_id,
                                'title': match.get('title'),
                                'price': match.get('price'),
                                'url': match.get('url')
                            })
                            print(f"✅ Found match on {other_platform}")
            
            # Return the product ID and cross-platform results
            return jsonify({
                'success': True,
                'message': 'Product scraped successfully',
                'product_id': product_id,
                'platform': platform,
                'cross_platform_matches': cross_platform_results
            })
        else:
            # Scraping failed - no success indicators found
            print(f"✗ Scraping failed - no success indicators found")
            return jsonify({'error': f'Scraping failed. Please check if the URL is correct.'}), 500

    except subprocess.TimeoutExpired as e:
        print(f"Timeout error: {str(e)}")
        return jsonify({'error': 'Scraping timeout. Please try again.'}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

# ==================== PRICE COMPARISON ROUTE ====================

@app.route('/api/compare-prices', methods=['POST'])
def compare_prices():
    """Compare prices across multiple platforms for the same product"""
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        
        if not product_name:
            return jsonify({'error': 'Product name is required'}), 400
        
        print(f"🔍 Searching for '{product_name}' across all platforms...")
        
        # Search across all platforms
        results = {
            'product_name': product_name,
            'platforms': [],
            'best_price': None,
            'best_platform': None,
            'price_difference': 0
        }
        
        platforms = ['amazon', 'flipkart', 'myntra', 'meesho']
        all_prices = []
        
        for platform in platforms:
            # Search in products collection for this platform
            search_filter = {
                'platform': platform,
                '$or': [
                    {'title': {'$regex': product_name, '$options': 'i'}},
                    {'name': {'$regex': product_name, '$options': 'i'}},
                    {'brand': {'$regex': product_name, '$options': 'i'}}
                ]
            }
            
            products = list(products_collection.find(search_filter).limit(5))
            
            if products:
                # Get the most relevant product (first match)
                product = serialize_doc(products[0])
                product_id = product.get('asin') or product.get('product_id')
                
                # Parse image
                image = ''
                if product.get('image'):
                    image = product.get('image')
                elif product.get('images') and isinstance(product.get('images'), list) and len(product.get('images')) > 0:
                    images = product.get('images')
                    valid_images = [img for img in images if img and '360_icon' not in img and 'SS40' not in img]
                    image = valid_images[0] if valid_images else images[0]
                elif product.get('image_url'):
                    image = product.get('image_url')
                
                current_price = parse_price(product.get('current_price') or product.get('price') or '0')
                original_price = parse_price(product.get('original_price') or '0')
                
                platform_data = {
                    'platform': platform,
                    'product_id': product_id,
                    'title': product.get('title') or product.get('name') or 'Unknown',
                    'image': image,
                    'current_price': current_price,
                    'original_price': original_price if original_price > 0 else None,
                    'discount': round(((original_price - current_price) / original_price * 100), 2) if original_price > current_price else 0,
                    'rating': parse_rating(product.get('rating')),
                    'reviews_count': parse_reviews_count(product.get('total_reviews')),
                    'url': product.get('url', ''),
                    'availability': True
                }
                
                results['platforms'].append(platform_data)
                if current_price > 0:
                    all_prices.append({'platform': platform, 'price': current_price})
            else:
                # Platform not available for this product
                results['platforms'].append({
                    'platform': platform,
                    'product_id': None,
                    'title': None,
                    'image': None,
                    'current_price': None,
                    'original_price': None,
                    'discount': 0,
                    'rating': None,
                    'reviews_count': None,
                    'url': None,
                    'availability': False
                })
        
        # Calculate best price
        if all_prices:
            best = min(all_prices, key=lambda x: x['price'])
            worst = max(all_prices, key=lambda x: x['price'])
            
            results['best_price'] = best['price']
            results['best_platform'] = best['platform']
            results['worst_price'] = worst['price']
            results['worst_platform'] = worst['platform']
            results['price_difference'] = round(worst['price'] - best['price'], 2)
            results['savings_percentage'] = round(((worst['price'] - best['price']) / worst['price'] * 100), 2) if worst['price'] > 0 else 0
        
        print(f"✅ Found prices on {len([p for p in results['platforms'] if p['availability']])} platforms")
        
        return jsonify(results)
    
    except Exception as e:
        print(f"❌ Price comparison error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ==================== AUTHENTICATION ROUTES ====================

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode JWT token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = users_collection.find_one({'_id': ObjectId(data['user_id'])})
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            # Add user to request context
            request.current_user = serialize_doc(current_user)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user with email and password"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Validate input
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = {
            'email': email,
            'name': name,
            'password': generate_password_hash(password),
            'auth_provider': 'email',
            'created_at': datetime.utcnow(),
            'last_login': datetime.utcnow()
        }
        
        result = users_collection.insert_one(user)
        user_id = str(result.inserted_id)
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'auth_provider': 'email'
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with email and password"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = users_collection.find_one({'email': email})
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user registered with Google
        if user.get('auth_provider') == 'google':
            return jsonify({'error': 'Please sign in with Google'}), 400
        
        # Verify password
        if not check_password_hash(user.get('password', ''), password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'auth_provider': user.get('auth_provider', 'email')
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Authenticate with Google OAuth"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Google token is required'}), 400
        
        # Verify Google token
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            # Get user info from Google
            email = idinfo['email'].lower().strip()
            name = idinfo.get('name', email.split('@')[0])
            google_id = idinfo['sub']
            picture = idinfo.get('picture', '')
            
        except ValueError as e:
            return jsonify({'error': 'Invalid Google token'}), 401
        
        # Check if user exists
        user = users_collection.find_one({'email': email})
        
        if user:
            # Update existing user
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {
                    'last_login': datetime.utcnow(),
                    'google_id': google_id,
                    'picture': picture
                }}
            )
            user_id = str(user['_id'])
        else:
            # Create new user
            new_user = {
                'email': email,
                'name': name,
                'google_id': google_id,
                'picture': picture,
                'auth_provider': 'google',
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            result = users_collection.insert_one(new_user)
            user_id = str(result.inserted_id)
        
        # Generate JWT token
        jwt_token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': jwt_token,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'picture': picture,
                'auth_provider': 'google'
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current authenticated user"""
    try:
        user = request.current_user
        return jsonify({
            'user': {
                'id': user['_id'],
                'email': user['email'],
                'name': user['name'],
                'picture': user.get('picture', ''),
                'auth_provider': user.get('auth_provider', 'email')
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """Logout user"""
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# ==================== END AUTHENTICATION ROUTES ====================

# API route to get product details
@app.route('/api/product/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product details from database"""
    try:
        # Try finding by ASIN first (Amazon)
        product = products_collection.find_one({'asin': product_id})
        id_field = 'asin'
        platform = 'amazon'
        
        # If not found, try product_id (Flipkart/Myntra/Meesho)
        if not product:
            product = products_collection.find_one({'product_id': product_id})
            id_field = 'product_id'
            # Determine platform from URL or stored platform field
            if product:
                if product.get('platform'):
                    platform = product.get('platform').lower()
                elif 'flipkart' in product.get('url', '').lower():
                    platform = 'flipkart'
                elif 'myntra' in product.get('url', '').lower():
                    platform = 'myntra'
                elif 'meesho' in product.get('url', '').lower():
                    platform = 'meesho'
                else:
                    platform = 'unknown'
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get price statistics
        price_stats = get_price_statistics(product_id, id_field)
        
        # Get recent reviews
        reviews = list(reviews_collection.find(
            {id_field: product_id}
        ).sort('scraped_at', -1).limit(10))
        
        # Serialize
        product = serialize_doc(product)
        reviews = [serialize_doc(r) for r in reviews]
        
        # Map different field names from scrapers to consistent format
        name = product.get('name') or product.get('title') or product.get('product_name') or ''
        description = product.get('description') or product.get('product_description') or ''
        image = ''
        
        # Handle image - could be single image or array
        if product.get('image'):
            image = product.get('image')
        elif product.get('images') and isinstance(product.get('images'), list) and len(product.get('images')) > 0:
            # Filter out small icons and 360 icons, prefer larger product images
            images = product.get('images')
            valid_images = [img for img in images if img and '360_icon' not in img and 'SS40' not in img]
            if valid_images:
                image = valid_images[0]
            else:
                image = images[0]  # Fallback to first image if no valid ones found
        elif product.get('image_url'):
            image = product.get('image_url')
        
        # Parse price - try current_price first, then price
        current_price_raw = product.get('current_price') or product.get('price') or '0'
        current_price = parse_price(current_price_raw)
        
        # Add parsed numeric fields for frontend
        product['rating'] = parse_rating(product.get('rating')) if product.get('rating') else None
        product['reviews_count'] = parse_reviews_count(product.get('total_reviews'))
        product['current_price'] = current_price
        
        # Also parse original_price if it exists
        if product.get('original_price'):
            product['original_price'] = parse_price(product.get('original_price'))
        else:
            product['original_price'] = None
        
        # Extract features from specifications
        if product.get('specifications'):
            if isinstance(product['specifications'], dict):
                features = []
                for key, value in product['specifications'].items():
                    features.append({key: str(value)})
                product['features'] = features
        
        # Ensure all required fields exist
        response_data = {
            '_id': product['_id'],
            'asin': product.get('asin'),
            'product_id': product.get('product_id'),
            'name': name,
            'title': name,  # Add title alias
            'description': description,
            'image': image,
            'current_price': current_price,
            'original_price': product.get('original_price'),
            'rating': product.get('rating'),
            'reviews_count': product.get('reviews_count', 0),
            'platform': platform,
            'url': product.get('url', ''),
            'features': product.get('features', []),
            'specifications': product.get('specifications', {}),
            'scraped_at': product.get('scraped_at') or product.get('last_updated') or product.get('first_seen') or '',
        }
        
        # Search for the same product on other platforms
        cross_platform_products = []
        brand = product.get('brand', '') or ''
        
        # Extract core product identity by removing filler words and variants
        # Need precise matching for products like "iPhone 17 Pro 256GB" vs "iPhone 16 Pro 256GB"
        stop_words = {'with', 'from', 'for', 'the', 'and', 'or', 'pack', 'size', 'set', 'of', 'in', 'on', 'at', 'by', 
                     'ml', 'gm', 'kg', 'grams', 'liters', 'broad', 'spectrum', 'touch', 'dry', 'pa', 'display', 
                     'promotion', 'upto', 'up', 'to', 'cm', 'inch'}
        
        # Model/version numbers are critical for matching (iPhone 16 vs 17, etc.)
        important_patterns = [r'\d+gb', r'\d+tb', r'\d+\s*gb', r'\d+\s*tb', r'\bpro\b', r'\bmax\b', r'\bplus\b', 
                             r'\bultra\b', r'\bmini\b', r'\d{2,4}', r'gen\s*\d+']
        
        # Extract meaningful words from product name
        key_words = []
        important_words = []  # Model numbers, capacities, variants
        
        if name:
            # Clean and normalize the name
            clean_name = re.sub(r'[^\w\s]', ' ', name.lower())
            words = clean_name.split()
            
            # Identify important identifiers (model numbers, capacities, variants)
            for word in words:
                # Check if word matches important patterns
                is_important = False
                for pattern in important_patterns:
                    if re.search(pattern, word):
                        is_important = True
                        break
                
                if is_important:
                    important_words.append(word)
                elif len(word) > 2 and word not in stop_words:
                    key_words.append(word)
            
            # Limit to top identifying words
            key_words = key_words[:4]
        
        # Add brand as priority keyword if available
        if brand and len(brand) > 2:
            brand_clean = brand.lower().strip()
            if brand_clean not in key_words:
                key_words.insert(0, brand_clean)
        
        # Combine: brand + model identifiers + key features
        all_search_terms = key_words + important_words
        
        print(f"\n🔍 Cross-Platform Search (Precise Matching)")
        print(f"   Product: {name[:70]}")
        print(f"   Current Platform: {platform.upper()}")
        print(f"   Key Words: {key_words[:5]}")
        print(f"   Important Identifiers: {important_words}")
        
        # Search on all platforms except the current one
        all_platforms = ['amazon', 'flipkart', 'myntra', 'meesho']
        other_platforms = [p for p in all_platforms if p != platform]
        
        for search_platform in other_platforms:
            matching = None
            
            if len(all_search_terms) >= 2:
                # Build query requiring ALL important identifiers to match
                # Example: "iPhone" + "17" + "Pro" + "256gb" must all be present
                
                query_conditions = []
                
                # ALL key words and important identifiers must match
                for term in all_search_terms[:6]:  # Limit to top 6 most important terms
                    query_conditions.append({
                        '$or': [
                            {'title': {'$regex': term, '$options': 'i'}},
                            {'name': {'$regex': term, '$options': 'i'}},
                            {'product_name': {'$regex': term, '$options': 'i'}},
                            {'brand': {'$regex': term, '$options': 'i'}}
                        ]
                    })
                
                # Add platform filter
                query_conditions.append({'platform': search_platform})
                
                # Execute search - ALL terms must match
                query = {'$and': query_conditions}
                print(f"   🔎 Searching {search_platform}: Matching ALL of {all_search_terms[:6]}")
                matching = products_collection.find_one(query)
                
                if matching:
                    match_name = matching.get('title') or matching.get('name') or matching.get('product_name') or ''
                    print(f"   ✅ {search_platform.upper()}: {match_name[:60]}")
                else:
                    print(f"   ❌ No exact match on {search_platform}")
            
            # If we found a match, add it to results
            if matching:
                match_id = matching.get('asin') or matching.get('product_id')
                match_price = parse_price(matching.get('current_price') or matching.get('price') or '0')
                match_title = matching.get('title') or matching.get('name') or matching.get('product_name') or ''
                
                # Parse image
                match_image = ''
                if matching.get('image'):
                    match_image = matching.get('image')
                elif matching.get('images') and isinstance(matching.get('images'), list) and len(matching.get('images')) > 0:
                    images = matching.get('images')
                    valid_images = [img for img in images if img and '360_icon' not in img and 'SS40' not in img]
                    match_image = valid_images[0] if valid_images else images[0]
                elif matching.get('image_url'):
                    match_image = matching.get('image_url')
                
                cross_platform_products.append({
                    'platform': search_platform,
                    'product_id': match_id,
                    'title': match_title,
                    'image': match_image,
                    'current_price': match_price,
                    'original_price': parse_price(matching.get('original_price') or '0') if matching.get('original_price') else None,
                    'rating': parse_rating(matching.get('rating')) if matching.get('rating') else None,
                    'reviews_count': parse_reviews_count(matching.get('total_reviews')),
                    'url': matching.get('url', '')
                })
                print(f"   📦 Added: {match_title[:40]}... (₹{match_price})")
            else:
                print(f"   ❌ No match found on {search_platform}")
        
        # Add cross-platform products to response
        if cross_platform_products:
            response_data['crossPlatformProducts'] = cross_platform_products
            print(f"📊 Total platforms found: {len(cross_platform_products) + 1}")
        else:
            print(f"⚠️  No cross-platform matches found (exact matching enabled)")
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API route to get price history
@app.route('/api/product/<product_id>/price-history', methods=['GET'])
def get_price_history(product_id):
    """Get price history for a product across all platforms"""
    try:
        # Determine ID field
        product = products_collection.find_one({'asin': product_id})
        if not product:
            product = products_collection.find_one({'product_id': product_id})
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        id_field = 'asin' if product.get('asin') else 'product_id'
        
        # Get query parameters
        period = request.args.get('period', 'daily')  # daily, weekly, monthly
        days = int(request.args.get('days', 30))
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get the source product's platform
        source_platform = product.get('platform', 'unknown')
        
        # Find cross-platform products using the same logic as product detail
        cross_platform_products = []
        name = product.get('title') or product.get('name') or product.get('product_name')
        brand = product.get('brand')
        
        # Extract keywords
        stop_words = {'with', 'from', 'for', 'the', 'and', 'or', 'pack', 'size', 'set', 'of', 'in', 'on', 'at', 'by',
                     'ml', 'gm', 'kg', 'grams', 'liters', 'broad', 'spectrum', 'touch', 'dry', 'pa'}
        
        key_words = []
        if name:
            clean_name = re.sub(r'[^\w\s]', ' ', name.lower())
            words = clean_name.split()
            key_words = [w for w in words if len(w) > 2 and w not in stop_words][:6]
        
        if brand and len(brand) > 2:
            brand_clean = brand.lower().strip()
            if brand_clean not in key_words:
                key_words.insert(0, brand_clean)
        
        # Search for matching products on other platforms
        all_platforms = ['amazon', 'flipkart', 'myntra', 'meesho']
        other_platforms = [p for p in all_platforms if p != source_platform]
        
        product_ids_by_platform = {source_platform: product_id}
        
        for search_platform in other_platforms:
            if key_words and len(key_words) >= 2:
                primary_word = key_words[0]
                secondary_word = key_words[1]
                
                query_conditions = [
                    {
                        '$or': [
                            {'title': {'$regex': primary_word, '$options': 'i'}},
                            {'name': {'$regex': primary_word, '$options': 'i'}},
                            {'product_name': {'$regex': primary_word, '$options': 'i'}},
                            {'brand': {'$regex': primary_word, '$options': 'i'}}
                        ]
                    },
                    {
                        '$or': [
                            {'title': {'$regex': secondary_word, '$options': 'i'}},
                            {'name': {'$regex': secondary_word, '$options': 'i'}},
                            {'product_name': {'$regex': secondary_word, '$options': 'i'}}
                        ]
                    },
                    {'platform': search_platform}
                ]
                
                query = {'$and': query_conditions}
                matching = products_collection.find_one(query)
                
                if matching:
                    match_id = matching.get('asin') or matching.get('product_id')
                    product_ids_by_platform[search_platform] = match_id
        
        # Now fetch price history for all platforms
        all_price_history = {}
        
        for platform, pid in product_ids_by_platform.items():
            # Determine the ID field for this product
            platform_product = products_collection.find_one({'asin': pid}) or products_collection.find_one({'product_id': pid})
            if not platform_product:
                continue
            
            pid_field = 'asin' if platform_product.get('asin') else 'product_id'
            
            # Query price history for this platform's product
            price_history = list(price_history_collection.find({
                pid_field: pid,
                'timestamp': {'$gte': start_date, '$lte': end_date}
            }).sort('timestamp', 1))
            
            # Store price history by date for this platform
            for entry in price_history:
                date_str = entry['timestamp'].strftime('%Y-%m-%d')
                price_numeric = entry.get('price_numeric')
                
                # Parse price if not already numeric
                if not price_numeric and entry.get('price'):
                    price_numeric = parse_price(entry.get('price'))
                
                if date_str not in all_price_history:
                    all_price_history[date_str] = {'date': date_str}
                
                all_price_history[date_str][platform] = price_numeric
        
        # Convert to list and sort by date
        formatted_history = list(all_price_history.values())
        formatted_history.sort(key=lambda x: x['date'])
        
        # Get price statistics for source product
        stats = get_price_statistics(product_id, id_field)
        
        return jsonify({
            'history': formatted_history,
            'stats': stats,
            'platforms': list(product_ids_by_platform.keys())
        })
    
    except Exception as e:
        print(f"Error in get_price_history: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper function to calculate price statistics
def get_price_statistics(product_id, id_field='asin'):
    """Calculate price statistics from price history"""
    try:
        # First try to get price records with price_numeric
        price_records = list(price_history_collection.find({
            id_field: product_id,
            'price_numeric': {'$exists': True, '$ne': None}
        }).sort('timestamp', -1))
        
        # If no price_numeric, try to parse from price string field
        if not price_records:
            price_records = list(price_history_collection.find({
                id_field: product_id,
                'price': {'$exists': True, '$ne': None}
            }).sort('timestamp', -1))
            
            # Parse the price strings
            for record in price_records:
                if 'price' in record and not record.get('price_numeric'):
                    record['price_numeric'] = parse_price(record['price'])
        
        if not price_records:
            # No price history, try to get from product itself
            product = products_collection.find_one({id_field: product_id})
            if product:
                # Try both 'current_price' and 'price' fields
                price_raw = product.get('current_price') or product.get('price')
                if price_raw:
                    current_price = parse_price(price_raw)
                    return {
                        'current_price': current_price,
                        'lowest_price': current_price,
                        'highest_price': current_price,
                        'average_price': current_price,
                        'price_drop_percentage': 0,
                        'total_records': 0
                    }
            
            return {
                'current_price': None,
                'lowest_price': None,
                'highest_price': None,
                'average_price': None,
                'price_drop_percentage': None
            }
        
        prices = [r['price_numeric'] for r in price_records if r.get('price_numeric')]
        
        if not prices:
            return {
                'current_price': None,
                'lowest_price': None,
                'highest_price': None,
                'average_price': None,
                'price_drop_percentage': None
            }
        
        current_price = prices[0]
        lowest_price = min(prices)
        highest_price = max(prices)
        average_price = sum(prices) / len(prices)
        
        # Calculate price drop percentage
        price_drop = None
        if highest_price > 0:
            price_drop = ((highest_price - current_price) / highest_price) * 100
        
        return {
            'current_price': current_price,
            'current_price_formatted': price_records[0].get('price'),
            'lowest_price': lowest_price,
            'highest_price': highest_price,
            'average_price': round(average_price, 2),
            'price_drop_percentage': round(price_drop, 2) if price_drop else 0,
            'total_records': len(price_records)
        }
    
    except Exception as e:
        print(f"Error calculating price stats: {e}")
        import traceback
        traceback.print_exc()
        return {}

# API route to get all reviews for a product
@app.route('/api/product/<product_id>/reviews', methods=['GET'])
def get_reviews(product_id):
    """Get all reviews for a product"""
    try:
        # Determine ID field
        product = products_collection.find_one({'asin': product_id})
        id_field = 'asin' if product else 'product_id'
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        
        # Query reviews
        reviews = list(reviews_collection.find({
            id_field: product_id
        }).sort('scraped_at', -1).skip(skip).limit(limit))
        
        total_reviews = reviews_collection.count_documents({id_field: product_id})
        
        # Serialize
        reviews = [serialize_doc(r) for r in reviews]
        
        return jsonify({
            'product_id': product_id,
            'reviews': reviews,
            'total': total_reviews,
            'page': page,
            'pages': (total_reviews + limit - 1) // limit
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API route to search products
@app.route('/api/products/search', methods=['GET'])
def search_products():
    """Search products by title or brand"""
    try:
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Search in title or brand
        search_filter = {
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'brand': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        products = list(products_collection.find(search_filter).skip(skip).limit(limit))
        total = products_collection.count_documents(search_filter)
        
        # Serialize and add price stats
        result_products = []
        for product in products:
            product = serialize_doc(product)
            product_id = product.get('asin') or product.get('product_id')
            id_field = 'asin' if product.get('asin') else 'product_id'
            
            # Parse image field - handle different formats
            image = ''
            if product.get('image'):
                image = product.get('image')
            elif product.get('images') and isinstance(product.get('images'), list) and len(product.get('images')) > 0:
                images = product.get('images')
                valid_images = [img for img in images if img and '360_icon' not in img and 'SS40' not in img]
                image = valid_images[0] if valid_images else images[0]
            elif product.get('image_url'):
                image = product.get('image_url')
            
            product['image'] = image
            product['title'] = product.get('name') or product.get('title') or product.get('product_name') or 'Unknown Product'
            product['price_stats'] = get_price_statistics(product_id, id_field)
            result_products.append(product)
        
        return jsonify({
            'products': result_products,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API route to get recent products
@app.route('/api/products/recent', methods=['GET'])
def get_recent_products():
    """Get recently scraped products"""
    try:
        limit = int(request.args.get('limit', 10))
        
        products = list(products_collection.find().sort('last_updated', -1).limit(limit))
        
        result_products = []
        for product in products:
            product = serialize_doc(product)
            product_id = product.get('asin') or product.get('product_id')
            id_field = 'asin' if product.get('asin') else 'product_id'
            
            # Extract image from images array if needed
            image = ''
            if product.get('image'):
                image = product.get('image')
            elif product.get('images') and isinstance(product.get('images'), list) and len(product.get('images')) > 0:
                # Filter out small icons and 360 icons, prefer larger product images
                images = product.get('images')
                valid_images = [img for img in images if img and '360_icon' not in img and 'SS40' not in img and '_SX38_' not in img and '_SY50_' not in img]
                if valid_images:
                    image = valid_images[0]
                else:
                    image = images[0]  # Fallback to first image if no valid ones found
            elif product.get('image_url'):
                image = product.get('image_url')
            
            product['image'] = image
            
            # Ensure name field exists (could be 'name' or 'title')
            if not product.get('name') and product.get('title'):
                product['name'] = product.get('title')
            
            # Parse price
            current_price_raw = product.get('current_price') or product.get('price') or '0'
            product['current_price'] = parse_price(current_price_raw)
            
            # Get price stats
            product['price_stats'] = get_price_statistics(product_id, id_field)
            
            result_products.append(product)
        
        return jsonify({'products': result_products})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API route to get statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    try:
        total_products = products_collection.count_documents({})
        total_price_records = price_history_collection.count_documents({})
        total_reviews = reviews_collection.count_documents({})
        
        # Get products by platform
        amazon_count = products_collection.count_documents({'spider': 'amazon'})
        flipkart_count = products_collection.count_documents({'spider': 'flipkart'})
        myntra_count = products_collection.count_documents({'spider': 'myntra'})
        
        return jsonify({
            'total_products': total_products,
            'total_price_records': total_price_records,
            'total_reviews': total_reviews,
            'by_platform': {
                'amazon': amazon_count,
                'flipkart': flipkart_count,
                'myntra': myntra_count
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API route to generate AI insights from reviews
@app.route('/api/product/<product_id>/ai-insights', methods=['GET'])
def get_ai_insights(product_id):
    """Generate AI-powered insights from product reviews and data"""
    try:
        # Get product
        product = products_collection.find_one({'asin': product_id})
        id_field = 'asin'
        if not product:
            product = products_collection.find_one({'product_id': product_id})
            id_field = 'product_id'
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get reviews
        reviews = list(reviews_collection.find({id_field: product_id}).limit(50))
        
        # Get price stats
        price_stats = get_price_statistics(product_id, id_field)
        
        # Analyze reviews for insights
        insights = analyze_reviews(reviews, product, price_stats)
        
        return jsonify(insights)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to analyze reviews and generate AI insights using Gemini
def analyze_reviews(reviews, product, price_stats):
    """Analyze reviews using Gemini AI to extract pros, cons, and buying recommendation"""
    
    # Get product details
    product_name = product.get('name') or product.get('title') or 'Product'
    product_rating = parse_rating(product.get('rating', '0'))
    review_count = len(reviews)
    current_price = price_stats.get('current_price', 0)
    
    # Check if Gemini API is configured
    if not GEMINI_API_KEY:
        print("⚠️ Gemini API key not configured. Using basic analysis.")
        return generate_basic_insights(reviews, product, price_stats)
    
    try:
        # Prepare review texts for analysis
        review_texts = []
        for review in reviews[:20]:  # Analyze up to 20 reviews
            text = review.get('review_text') or review.get('text') or ''
            rating_str = review.get('rating', '0')
            rating = parse_rating(rating_str)
            if text and len(text) > 20:
                review_texts.append(f"[Rating: {rating}/5] {text[:500]}")
        
        if not review_texts:
            print("⚠️ No review texts available. Using basic analysis.")
            return generate_basic_insights(reviews, product, price_stats)
        
        # Create comprehensive prompt for Gemini
        reviews_combined = "\n\n".join(review_texts[:15])  # Limit to prevent token overflow
        
        prompt = f"""Analyze the following product and its customer reviews to provide comprehensive buying insights:

Product Name: {product_name}
Current Price: ₹{current_price:,.0f}
Average Rating: {product_rating:.1f}/5 stars
Total Reviews: {review_count}

Customer Reviews:
{reviews_combined}

Please provide a detailed analysis in the following JSON format:
{{
  "summary": "A comprehensive 2-3 sentence summary of the product based on reviews, highlighting overall customer sentiment and key value propositions",
  "pros": ["List 4-6 specific positive aspects mentioned by customers"],
  "cons": ["List 3-5 specific concerns or drawbacks mentioned by customers"],
  "recommendation_score": "A score from 1-10 based on overall quality, value, and customer satisfaction",
  "buy_recommendation": "Should I buy this product? Provide a clear YES or NO recommendation",
  "buy_reasoning": "2-3 sentences explaining why you recommend buying or not buying this product, considering price, quality, reviews, and value for money",
  "target_buyer": "Who is this product best suited for? (e.g., 'budget-conscious buyers', 'professionals', 'students')",
  "key_considerations": ["2-3 important factors to consider before purchasing"]
}}

Be honest, specific, and base your analysis strictly on the review data provided. Focus on recurring themes in customer feedback."""

        # Initialize Gemini model
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        
        # Generate AI insights
        print(f"🤖 Generating AI insights for {product_name}...")
        response = model.generate_content(prompt)
        
        # Parse response
        response_text = response.text
        
        # Extract JSON from response (handle markdown code blocks)
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        
        ai_analysis = json.loads(response_text)
        
        print(f"✓ AI insights generated successfully")
        
        # Format the response
        return {
            'insights': ai_analysis.get('summary', ''),
            'pros': ai_analysis.get('pros', []),
            'cons': ai_analysis.get('cons', []),
            'recommendation': ai_analysis.get('buy_reasoning', ''),
            'recommendation_score': int(ai_analysis.get('recommendation_score', 7)),
            'buy_recommendation': ai_analysis.get('buy_recommendation', 'MAYBE'),
            'target_buyer': ai_analysis.get('target_buyer', 'General consumers'),
            'key_considerations': ai_analysis.get('key_considerations', []),
            'total_reviews_analyzed': review_count,
            'average_rating': round(product_rating, 1),
            'ai_generated': True
        }
        
    except Exception as e:
        print(f"❌ Error generating AI insights: {str(e)}")
        import traceback
        traceback.print_exc()
        return generate_basic_insights(reviews, product, price_stats)

# Helper function for basic insights when AI is unavailable
def generate_basic_insights(reviews, product, price_stats):
    """Generate basic insights without AI when Gemini is unavailable"""
    
    # Extract pros and cons from reviews
    pros = []
    cons = []
    
    for review in reviews[:10]:  # Analyze top 10 reviews
        text = review.get('review_text') or review.get('text') or ''
        rating_str = review.get('rating', '0')
        rating = parse_rating(rating_str)
        
        # Extract snippets based on rating
        if rating >= 4 and text and len(pros) < 5:
            snippet = text[:100].split('.')[0] if '.' in text[:100] else text[:100]
            if snippet and len(snippet) > 20:
                pros.append(snippet.strip() + ('...' if len(text) > 100 else ''))
        
        if rating <= 2 and text and len(cons) < 5:
            snippet = text[:100].split('.')[0] if '.' in text[:100] else text[:100]
            if snippet and len(snippet) > 20:
                cons.append(snippet.strip() + ('...' if len(text) > 100 else ''))
    
    # Default pros and cons if not enough from reviews
    if not pros:
        pros = [
            'Quality product from reliable brand',
            'Good customer ratings',
            'Popular choice among buyers',
            'Available for immediate purchase'
        ]
    
    if not cons:
        cons = [
            'Limited long-term user reviews',
            'Price may vary across platforms',
            'Consider comparing with similar products'
        ]
    
    # Get product rating
    product_rating = parse_rating(product.get('rating', '0'))
    review_count = len(reviews)
    
    # Generate insights text
    rating_text = f"{product_rating:.1f}/5" if product_rating > 0 else "Not rated"
    
    insights_text = f"This product has {review_count} customer reviews with an average rating of {rating_text}. "
    
    # Add price information
    if price_stats.get('current_price'):
        current = price_stats['current_price']
        insights_text += f"Currently priced at ₹{current:,.0f}. "
        
        if price_stats.get('price_drop_percentage', 0) > 5:
            insights_text += f"Great deal - price dropped by {price_stats['price_drop_percentage']:.0f}%! "
        elif price_stats.get('lowest_price') and current == price_stats['lowest_price']:
            insights_text += "Currently at its lowest recorded price! "
    
    # Generate recommendation
    recommendation_score = min(10, max(1, round(product_rating * 2)))
    
    if recommendation_score >= 8:
        recommendation = "Highly recommended based on positive customer feedback. "
        buy_recommendation = "YES"
    elif recommendation_score >= 6:
        recommendation = "Good choice with satisfied customers. "
        buy_recommendation = "MAYBE"
    else:
        recommendation = "Mixed reviews - please read customer feedback carefully. "
        buy_recommendation = "CONSIDER ALTERNATIVES"
    
    if price_stats.get('price_drop_percentage', 0) > 10:
        recommendation += f"Currently {price_stats['price_drop_percentage']:.0f}% off - great time to buy!"
    
    return {
        'insights': insights_text,
        'pros': pros,
        'cons': cons,
        'recommendation': recommendation,
        'recommendation_score': recommendation_score,
        'buy_recommendation': buy_recommendation,
        'target_buyer': 'General consumers',
        'key_considerations': ['Check product specifications', 'Compare prices across platforms', 'Read detailed reviews'],
        'total_reviews_analyzed': review_count,
        'average_rating': round(product_rating, 1),
        'ai_generated': False
    }

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB connection
        client.admin.command('ping')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# API route to get review insights using Gemini AI
@app.route('/api/product/<product_id>/review-insights', methods=['GET'])
def get_review_insights(product_id):
    """Generate AI-powered review insights using Gemini"""
    try:
        # Check if Gemini API is configured
        if not GEMINI_API_KEY:
            return jsonify({'error': 'Gemini API key not configured'}), 500
        
        # Determine ID field
        product = products_collection.find_one({'asin': product_id})
        id_field = 'asin' if product else 'product_id'
        
        if not product:
            product = products_collection.find_one({'product_id': product_id})
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get all reviews for this product
        reviews = list(reviews_collection.find({
            id_field: product_id
        }).sort('scraped_at', -1).limit(100))  # Analyze up to 100 recent reviews
        
        if not reviews:
            return jsonify({'error': 'No reviews found for this product'}), 404
        
        # Prepare review text for analysis
        review_texts = []
        for review in reviews:
            text = review.get('review_text', '')
            rating = review.get('rating', '')
            if text:
                review_texts.append(f"Rating: {rating}\nReview: {text}")
        
        if not review_texts:
            return jsonify({'error': 'No review text available for analysis'}), 404
        
        # Limit to first 50 reviews for API efficiency
        review_sample = "\n\n---\n\n".join(review_texts[:50])
        
        # Create prompt for Gemini
        product_name = product.get('title', 'this product')
        prompt = f"""Analyze the following customer reviews for {product_name} and provide detailed insights in JSON format.

Reviews:
{review_sample}

Please analyze these reviews and provide a JSON response with the following structure:
{{
    "overall_sentiment": {{
        "positive": <percentage 0-100>,
        "neutral": <percentage 0-100>,
        "negative": <percentage 0-100>
    }},
    "key_topics": [
        {{
            "topic": "<topic name like Battery Life, Camera, Build Quality, etc>",
            "sentiment": <score between -1 and 1, where 1 is very positive, 0 is neutral, -1 is very negative>,
            "mentions": <number of times mentioned>
        }}
    ],
    "controversy_score": <0-100, where 100 means highly controversial/mixed opinions>,
    "reliability_score": <0-100, based on verified purchases and review authenticity>,
    "ai_confidence": <0-100, your confidence in this analysis>
}}

Key topics should focus on: Battery Life, Build Quality, Camera Quality, Price/Value, Performance, Display, Design, Durability, Features, Customer Service.
Return ONLY valid JSON, no additional text."""

        # Call Gemini API
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        response = model.generate_content(prompt)
        
        # Parse response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        insights_data = json.loads(response_text)
        
        # Add metadata
        insights_data['product_id'] = product_id
        insights_data['product_name'] = product_name
        insights_data['total_reviews_analyzed'] = len(review_texts[:50])
        insights_data['generated_at'] = datetime.now().isoformat()
        
        return jsonify(insights_data)
    
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {str(e)}")
        print(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
        return jsonify({'error': 'Failed to parse AI response'}), 500
    except Exception as e:
        print(f"Error generating insights: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate insights: {str(e)}'}), 500

# API route for chatbot queries
@app.route('/api/chatbot', methods=['POST'])
def chatbot_query():
    """Handle chatbot queries using Gemini AI"""
    try:
        data = request.json
        query = data.get('query', '')
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        conversation_history = data.get('conversation_history', [])
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Check if Gemini API is configured
        if not GEMINI_API_KEY:
            return jsonify({
                'response': 'Sorry, the AI chatbot is currently unavailable. Please configure the Gemini API key to enable intelligent responses.',
                'ai_generated': False
            })
        
        # Build context based on product
        context = ""
        if product_id:
            # Get product details
            product = products_collection.find_one({'asin': product_id})
            if not product:
                product = products_collection.find_one({'product_id': product_id})
            
            if product:
                product_name = product.get('name') or product.get('title') or product_name
                price = product.get('current_price') or product.get('price')
                rating = product.get('rating')
                platform = product.get('platform', 'Unknown')
                
                context = f"""
Product Information:
- Name: {product_name}
- Current Price: ₹{parse_price(price) if price else 'N/A'}
- Rating: {rating}
- Platform: {platform}

"""
                # Get recent reviews for context
                reviews = list(reviews_collection.find({
                    'asin' if product.get('asin') else 'product_id': product_id
                }).sort('scraped_at', -1).limit(5))
                
                if reviews:
                    context += "Recent Customer Reviews:\n"
                    for review in reviews[:3]:
                        text = review.get('review_text') or review.get('text', '')
                        if text:
                            context += f"- {text[:200]}...\n"
                    context += "\n"
                
                # Get AI insights if available
                price_stats = get_price_statistics(product_id, 'asin' if product.get('asin') else 'product_id')
                if price_stats:
                    context += f"""Price Information:
- Current Price: ₹{price_stats.get('current_price', 0):,.0f}
- Lowest Price: ₹{price_stats.get('lowest_price', 0):,.0f}
- Highest Price: ₹{price_stats.get('highest_price', 0):,.0f}
- Average Price: ₹{price_stats.get('average_price', 0):,.2f}
- Price Drop: {price_stats.get('price_drop_percentage', 0):.1f}%

"""
        
        # Build conversation history
        conversation_text = ""
        for msg in conversation_history[-6:]:  # Last 3 exchanges
            role = "User" if msg.get('role') == 'user' else "Assistant"
            conversation_text += f"{role}: {msg.get('content')}\n"
        
        # Create comprehensive prompt
        prompt = f"""You are an AI shopping assistant for PricePilot, a price comparison platform that tracks products across Amazon, Flipkart, and Myntra.

{context}

Previous Conversation:
{conversation_text if conversation_text else 'This is the start of the conversation.'}

User Question: {query}

Guidelines:
1. Be helpful, friendly, and concise (2-3 sentences max)
2. Use the product information and reviews provided above to give accurate answers
3. If asked about price, mention the current price and any deals
4. If asked about recommendations, consider ratings, reviews, and price trends
5. If asked about features, refer to the product information
6. If you don't have specific information, say so honestly
7. Always encourage comparing prices across platforms (Amazon, Flipkart, Myntra)
8. Use emojis occasionally to make responses friendly 😊
9. For "should I buy" questions, give balanced pros/cons based on data

Response (be natural and conversational):"""

        # Call Gemini API
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        ai_response = response.text.strip()
        
        print(f"💬 Chatbot query: {query[:50]}...")
        print(f"🤖 AI response: {ai_response[:100]}...")
        
        return jsonify({
            'response': ai_response,
            'ai_generated': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Chatbot error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback response
        return jsonify({
            'response': "I'm having trouble processing that right now. Could you try rephrasing your question? 🤔",
            'ai_generated': False
        }), 200

# This allows you to run the app directly
if __name__ == '__main__':
    # Disable reloader to avoid Windows socket issues
    app.run(debug=True, port=5000, use_reloader=False)

