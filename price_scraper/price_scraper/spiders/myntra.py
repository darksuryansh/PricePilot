# scrapy crawl myntra -a url="https://www.myntra.com/..." -o myntra.json
#  scrapy crawl myntra -a url="https://www.myntra.com/watches/michael+kors/michael-kors-women-rose-gold-pyper-analogue-watch-mk3897/10899600/buy" -o myntra.json                                                                                                                                                                                             

import re
import json
import os
import scrapy
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class MyntraSpider(scrapy.Spider):
    name = "myntra"

    def __init__(self, url=None, product_id=None, api_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.url = url
        
        # Get API key from command line argument or environment variable
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        
        # Extract product_id from URL if not provided
        if url and not product_id:
            # Myntra URLs: https://www.myntra.com/kurtas/jompers/product-name/27638086/buy
            # Extract the number before /buy
            product_id_match = re.search(r'/(\d{6,})/buy', url)
            if not product_id_match:
                # Alternative: last number in URL
                product_id_match = re.search(r'/(\d{6,})', url)
            
            self.product_id = product_id_match.group(1) if product_id_match else None
        else:
            self.product_id = product_id
        
        if not url and not product_id:
            raise ValueError("Either URL or product_id must be provided")
        
        if self.api_key:
            self.logger.info("✓ API key loaded successfully")
        else:
            self.logger.warning("⚠ No API key provided - will skip API calls")
        
        self.human_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

    def start_requests(self):
        """Start scraping - try API first, fallback to web scraping"""
        
        # Skip API for now since it's returning 500
        # If you want to try API: uncomment below
        # if self.api_key:
        #     self.logger.info(f"🔍 Trying Agent Commerce API for: {self.url}")
        #     api_data = self.get_api_data(self.url)
        #     if api_data:
        #         self.logger.info("✅ API data received successfully")
        #         yield api_data
        #         return
        
        # Go straight to web scraping with scrolling to load reviews
        if self.url:
            self.logger.info(f"🌐 Scraping Myntra product page")
            
            # Prepare request meta
            request_meta = {
                "playwright": True,
                "playwright_context": "default",
                "playwright_page_goto_kwargs": {
                    "wait_until": "domcontentloaded",
                    "timeout": 30000,
                },
                "playwright_page_methods": [
                    # Wait for dynamic content
                    ("wait_for_timeout", 3000),
                    # Scroll to middle of page
                    ("evaluate", "window.scrollTo(0, document.body.scrollHeight / 2)"),
                    ("wait_for_timeout", 2000),
                    # Scroll to bottom to load reviews
                    ("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    ("wait_for_timeout", 2000),
                ],
                "playwright_include_page": True,
            }
            
            # Proxy is now configured in settings.py at the context level
            # No need to set it in request meta
            
            yield scrapy.Request(
                self.url,
                callback=self.parse,
                dont_filter=True,
                meta=request_meta,
                errback=self.errback_handler
            )

    def get_api_data(self, product_url):
        """Fetch product data from Agent Commerce Audit API"""
        
        api_url = "https://agent-commerce-audit1.p.rapidapi.com/audit"
        
        headers = {
            "Content-Type": "application/json",
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "agent-commerce-audit1.p.rapidapi.com"
        }
        
        payload = {
            "url": product_url
        }
        
        try:
            self.logger.info(f"📡 Calling Agent Commerce API...")
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"API Response received")
            
            return self.process_api_response(data, product_url)
            
        except Exception as e:
            self.logger.error(f"❌ API request failed: {e}")
            return None

    def process_api_response(self, api_data, product_url):
        """Process data from API"""
        
        # Extract product ID
        product_id_match = re.search(r'/(\d{6,})/buy', product_url)
        if not product_id_match:
            product_id_match = re.search(r'/(\d{6,})', product_url)
        product_id = product_id_match.group(1) if product_id_match else None
        
        product_data = api_data.get('data', {}) or api_data
        
        title = product_data.get('title') or product_data.get('name')
        brand = product_data.get('brand')
        
        price_data = product_data.get('price', {})
        if isinstance(price_data, dict):
            price = price_data.get('discounted') or price_data.get('mrp')
            original_price = price_data.get('mrp')
            discount = price_data.get('discount')
        else:
            price = product_data.get('discounted_price') or product_data.get('price')
            original_price = product_data.get('mrp')
            discount = product_data.get('discount')
        
        price_numeric = self._extract_price(price)
        
        availability = "In Stock" if product_data.get('in_stock', True) else "Out of Stock"
        
        rating = product_data.get('rating') or product_data.get('average_rating')
        total_reviews = product_data.get('reviews_count')
        total_ratings = product_data.get('ratings_count')
        
        images = product_data.get('images', [])
        if not isinstance(images, list):
            images = [images] if images else []
        
        description = product_data.get('description')
        specifications = product_data.get('specifications', {})
        sizes = product_data.get('sizes', [])
        colors = product_data.get('colors', [])
        
        result = {
            "product_id": product_id,
            "url": product_url,
            "title": title,
            "brand": brand,
            "price": price,
            "price_numeric": price_numeric,
            "original_price": original_price,
            "discount": discount,
            "availability": availability,
            "rating": float(rating) if rating else None,
            "total_reviews": int(total_reviews) if total_reviews else None,
            "total_ratings": int(total_ratings) if total_ratings else None,
            "images": images,
            "description": description,
            "specifications": specifications,
            "sizes": sizes,
            "colors": colors,
            "reviews_from_page": [],
            "data_source": "agent_commerce_api"
        }
        
        self.logger.info(f"✅ Processed: {title}")
        return result

    def parse(self, response):
        """Parse data from Myntra web page"""
        
        # Check for error page or bot detection
        page_title = response.css("title::text").get()
        body_text = response.css("body").get()
        
        if not page_title or not body_text:
            self.logger.error("❌ Empty response received - page didn't load")
            return
        
        # Check for common error indicators
        error_indicators = ['oops', 'something went wrong', 'error', 'access denied', 'captcha']
        if any(indicator in page_title.lower() for indicator in error_indicators if page_title):
            self.logger.error(f"❌ Error page detected: {page_title}")
            self.logger.error("⚠️ Myntra may have detected bot activity. Try:")
            self.logger.error("   1. Using residential proxies")
            self.logger.error("   2. Reducing scraping frequency")
            self.logger.error("   3. Using Myntra's official API if available")
            return
        
        # Save HTML for debugging
        import os
        debug_dir = os.path.join(os.path.dirname(__file__), '../../debug')
        os.makedirs(debug_dir, exist_ok=True)
        debug_file = os.path.join(debug_dir, 'myntra_scrapy_response.html')
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        self.logger.info(f"💾 Saved HTML to {debug_file} ({len(response.text)} bytes)")
        
        # Extract product ID - FIXED
        product_id_match = re.search(r'/(\d{6,})/buy', self.url)
        if not product_id_match:
            product_id_match = re.search(r'/(\d{6,})', self.url)
        
        product_id = product_id_match.group(1) if product_id_match else None

        if not product_id:
            self.logger.error(f"❌ Could not extract product ID from URL: {self.url}")
            self.logger.error(f"URL structure: Please use format like /27638086/buy")
            return

        self.logger.info(f"✅ Processing Myntra Product ID: {product_id}")

        # Scrape from page (after scrolling done by playwright_page_methods)
        scraped_data = self.scrape_from_page(response, product_id)
        
        # Debug: Log what was extracted
        self.logger.info(f"📦 Scraped data summary:")
        self.logger.info(f"   Title: {scraped_data.get('title')[:50] if scraped_data.get('title') else 'None'}...")
        self.logger.info(f"   Brand: {scraped_data.get('brand')}")
        self.logger.info(f"   Price: {scraped_data.get('price')}")
        self.logger.info(f"   Images: {len(scraped_data.get('images', []))}")
        self.logger.info(f"   Description: {len(scraped_data.get('description', ''))} chars")
        self.logger.info(f"   Reviews: {len(scraped_data.get('reviews_from_page', []))}")
        
        # Build final result
        combined_data = {
            "product_id": product_id,
            "url": self.url,
            "platform": "myntra",  # Add platform identifier
            "title": scraped_data.get("title"),
            "brand": scraped_data.get("brand"),
            "price": scraped_data.get("price"),
            "price_numeric": scraped_data.get("price_numeric"),
            "original_price": scraped_data.get("original_price"),
            "discount": scraped_data.get("discount"),
            "availability": scraped_data.get("availability"),
            "rating": scraped_data.get("rating"),
            "total_reviews": scraped_data.get("total_reviews"),
            "total_ratings": scraped_data.get("total_ratings"),
            "images": scraped_data.get("images", []),
            "description": scraped_data.get("description"),
            "specifications": scraped_data.get("specifications", {}),
            "sizes": scraped_data.get("sizes", []),
            "colors": scraped_data.get("colors", []),
            "reviews_from_page": scraped_data.get("reviews_from_page", []),
            "data_source": "web_scraping"
        }

        yield combined_data

    def scrape_from_page(self, response, product_id):
        """Scrape product data from Myntra page"""
        
        self.logger.info(f"🔍 Parsing Myntra page for product {product_id}")
        
        # Log page title to verify page loaded
        page_title = response.css("title::text").get()
        self.logger.info(f"Page title: {page_title}")
        
        # Title and Brand - Myntra shows Brand first, then product name
        # Try multiple selectors for title/brand
        title = None
        brand = None
        
        # Method 1: Standard pdp-title/pdp-name
        title_parts = response.css("h1.pdp-title::text, h1.pdp-name::text").getall()
        if title_parts:
            title = " ".join([t.strip() for t in title_parts if t.strip()])
            brand = title_parts[0].strip() if title_parts else None
            self.logger.info(f"✓ Found title (method 1): {title}")
        
        # Method 2: Try any h1 on page
        if not title:
            h1_text = response.css("h1::text").getall()
            if h1_text:
                title = " ".join([t.strip() for t in h1_text if t.strip()])
                brand = h1_text[0].strip() if h1_text else None
                self.logger.info(f"✓ Found title (method 2 - h1): {title}")
        
        # Method 3: Look for data-react-helmet or meta tags
        if not title:
            title = response.css("meta[property='og:title']::attr(content)").get()
            if title:
                self.logger.info(f"✓ Found title (method 3 - meta): {title}")
                # Extract brand from title if present
                brand_match = re.match(r'^([A-Za-z\s&]+)\s+-\s+', title)
                if brand_match:
                    brand = brand_match.group(1).strip()
        
        # Method 4: Check JSON-LD structured data
        if not title:
            json_ld = response.css('script[type="application/ld+json"]::text').get()
            if json_ld:
                try:
                    data = json.loads(json_ld)
                    title = data.get('name')
                    brand = data.get('brand', {}).get('name') if isinstance(data.get('brand'), dict) else data.get('brand')
                    if title:
                        self.logger.info(f"✓ Found title (method 4 - JSON-LD): {title}")
                except:
                    pass
        
        if not title:
            self.logger.warning(f"⚠️ Could not extract title from page")
            # Log a snippet of the HTML to debug
            html_snippet = response.css("body").get()[:500] if response.css("body").get() else "No body found"
            self.logger.warning(f"HTML snippet: {html_snippet}")
        else:
            self.logger.info(f"✓ Title: {title}")
            self.logger.info(f"✓ Brand: {brand}")
        
        # Price - Try multiple selectors
        price = None
        original_price = None
        discount = None
        
        # Method 1: Standard pdp-price selectors
        price = response.css("span.pdp-price strong::text, div.pdp-price strong::text").get()
        original_price = response.css("span.pdp-mrp::text, span.pdp-discount-price::text").get()
        discount = response.css("span.pdp-discount::text").get()
        
        # Method 2: Try price-related classes
        if not price:
            price = response.css("[class*='price'] strong::text, [class*='Price'] strong::text").get()
            self.logger.info(f"✓ Found price (method 2): {price}")
        
        # Method 3: Check structured data
        if not price:
            json_ld = response.css('script[type="application/ld+json"]::text').get()
            if json_ld:
                try:
                    data = json.loads(json_ld)
                    offers = data.get('offers', {})
                    if isinstance(offers, dict):
                        price = offers.get('price')
                        if price:
                            price = f"₹{price}"
                            self.logger.info(f"✓ Found price (method 3 - JSON-LD): {price}")
                except:
                    pass
        
        if price:
            self.logger.info(f"✓ Price: {price}")
        else:
            self.logger.warning(f"⚠️ Could not extract price from page")
        
        price_numeric = self._extract_price(price)
        
        # Availability
        availability = "In Stock"
        if response.css(".size-buttons-out-of-stock, .pdp-notAvailable").get():
            availability = "Out of Stock"
        
        # Rating and Reviews
        rating = response.css("div.index-overallRating div::text, span.index-overallRating::text").get()
        
        # Total ratings and reviews - Try multiple selectors and methods
        ratings_text = response.css("div.index-ratingsCount::text, span.index-ratingsCount::text, .index-ratingsCount::text").get()
        reviews_text = response.css("div.index-reviewsCount::text, span.index-reviewsCount::text, .index-reviewsCount::text").get()
        
        # Look for ratings/reviews in the entire ratings section
        ratings_section_text = " ".join(response.css(".index-ratingsContainer *::text, [class*='rating'] *::text, [class*='review'] *::text").getall())
        
        total_ratings = None
        total_reviews = None
        
        # Parse ratings count
        if ratings_text:
            # Check if it contains "Ratings" keyword
            if 'Rating' in ratings_text:
                ratings_match = re.search(r'([\d,\.]+[kK]?)\s*Rating', ratings_text)
            else:
                ratings_match = re.search(r'([\d,\.]+[kK]?)', ratings_text)
            
            if ratings_match:
                rating_str = ratings_match.group(1).replace(',', '')
                if 'k' in rating_str.lower():
                    total_ratings = int(float(rating_str.replace('k', '').replace('K', '')) * 1000)
                else:
                    total_ratings = int(float(rating_str))
        
        # Parse reviews count - Try multiple sources
        if reviews_text:
            # Check if it contains "Reviews" keyword
            if 'Review' in reviews_text:
                reviews_match = re.search(r'([\d,\.]+[kK]?)\s*Review', reviews_text)
            else:
                reviews_match = re.search(r'([\d,\.]+[kK]?)', reviews_text)
            
            if reviews_match:
                review_str = reviews_match.group(1).replace(',', '')
                if 'k' in review_str.lower():
                    total_reviews = int(float(review_str.replace('k', '').replace('K', '')) * 1000)
                else:
                    total_reviews = int(float(review_str))
        
        # If reviews not found separately, search in the combined ratings section
        if not total_reviews and ratings_section_text:
            # Look for patterns like "Customer Reviews ( 486 )", "486 Reviews", "2.8k Reviews", etc.
            reviews_match = re.search(r'Customer Reviews\s*\(\s*([\d,\.]+[kK]?)\s*\)', ratings_section_text)
            if not reviews_match:
                reviews_match = re.search(r'([\d,\.]+[kK]?)\s*Review', ratings_section_text)
            
            if reviews_match:
                review_str = reviews_match.group(1).replace(',', '')
                if 'k' in review_str.lower():
                    total_reviews = int(float(review_str.replace('k', '').replace('K', '')) * 1000)
                else:
                    total_reviews = int(float(review_str))
        
        # Also check if ratings text has both (format: "2.8k Ratings & 486 Reviews")
        if not total_reviews and ratings_text and 'Review' in ratings_text:
            reviews_match = re.search(r'&\s*([\d,\.]+[kK]?)\s*Review', ratings_text)
            if reviews_match:
                review_str = reviews_match.group(1).replace(',', '')
                if 'k' in review_str.lower():
                    total_reviews = int(float(review_str.replace('k', '').replace('K', '')) * 1000)
                else:
                    total_reviews = int(float(review_str))
        
        # Availability
        images = []
        
        # Method 1: Standard image grid
        img_srcs = response.css("div.image-grid-image img::attr(src), div.image-grid-image img::attr(data-src)").getall()
        images.extend(img_srcs)
        
        # Method 2: Picture elements
        picture_srcs = response.css("picture img::attr(src), picture source::attr(srcset)").getall()
        images.extend(picture_srcs)
        
        # Method 3: Any images in image containers
        container_imgs = response.css(".image-grid-container img::attr(src), .image-grid-container img::attr(data-src)").getall()
        images.extend(container_imgs)
        
        # Method 4: Style backgrounds
        style_imgs = response.css("[style*='background-image']::attr(style)").getall()
        for style in style_imgs:
            url_match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
            if url_match:
                images.append(url_match.group(1))
        
        # Clean and deduplicate images, prioritize larger sizes
        cleaned_images = []
        for img in images:
            if img and 'http' in img:
                # Clean srcset format (remove size descriptors)
                img_url = img.split(' ')[0] if ' ' in img else img
                
                # Upgrade to higher quality - Myntra image URLs pattern
                # Replace small dimensions with larger ones
                img_url = re.sub(r'/(\d+)x(\d+)/', '/1080x1440/', img_url)  # Standard product images
                img_url = re.sub(r'/w_(\d+),h_(\d+)/', '/w_1080,h_1440/', img_url)  # Alternative format
                
                # Filter out known thumbnails
                if not any(thumb in img_url for thumb in ['150x150', '200x200', '50x50', '125x125']):
                    if img_url not in cleaned_images:
                        cleaned_images.append(img_url)
        
        images = cleaned_images
        
        self.logger.info(f"Found {len(images)} images")
        
        # Description - Try multiple selectors
        description_parts = []
        
        # Method 1: Product description content
        desc1 = response.css("div.pdp-product-description-content p::text, div.pdp-product-description-content::text").getall()
        description_parts.extend(desc1)
        
        # Method 2: Description section
        desc2 = response.css("div.pdp-description-content::text, div.pdp-description-content p::text").getall()
        description_parts.extend(desc2)
        
        # Method 3: Product details
        desc3 = response.css(".pdp-productDescriptorsContainer p::text, .pdp-productDescriptorsContainer div::text").getall()
        description_parts.extend(desc3)
        
        # Method 4: Any description divs
        desc4 = response.css("[class*='description'] p::text, [class*='Description'] p::text").getall()
        description_parts.extend(desc4)
        
        # Clean and join
        description = " ".join([d.strip() for d in description_parts if d.strip() and len(d.strip()) > 10])
        
        self.logger.info(f"Description length: {len(description)} characters")
        
        # Specifications
        specs = {}
        spec_items = response.css("div.index-row")
        for item in spec_items:
            key = item.css("div.index-rowKey::text").get()
            value = item.css("div.index-rowValue::text").get()
            if key and value:
                specs[key.strip()] = value.strip()
        
        # Sizes
        sizes = response.css("button.size-buttons-size-button p::text").getall()
        sizes = [s.strip() for s in sizes if s.strip()]
        
        # Colors
        colors = []
        
        # Reviews - Try multiple methods
        reviews = []
        
        # Method 1: Standard review containers
        review_containers = response.css("div.user-review-main, div.detailed-reviews-userReviewsContainer, [class*='user-review'], [class*='UserReview']")
        
        self.logger.info(f"Found {len(review_containers)} review containers")
        
        for review in review_containers:
            review_title = review.css("div.user-review-title::text, div.user-review-reviewTitle::text, [class*='reviewTitle']::text").get()
            rating_elem = review.css("div.user-review-rating::text, span.user-review-rating::text, [class*='rating']::text").get()
            review_text = review.css("div.user-review-reviewTextWrapper::text, div.user-review-commentText::text, [class*='commentText']::text, [class*='reviewText']::text").get()
            author = review.css("div.user-review-left::text, div.user-review-reviewerName::text, [class*='reviewerName']::text").get()
            
            if review_text and len(review_text.strip()) > 10:
                reviews.append({
                    "title": review_title.strip() if review_title else None,
                    "rating": rating_elem.strip() if rating_elem else None,
                    "text": review_text.strip(),
                    "author": author.strip() if author else "Anonymous",
                    "verified_purchase": True
                })
        
        # Method 2: If no reviews found, try alternative structure
        if len(reviews) == 0:
            self.logger.info("Trying alternative review selectors...")
            alt_reviews = response.css("[class*='review-card'], [class*='Review-card'], [data-review]")
            for review in alt_reviews:
                review_text = " ".join(review.css("::text").getall())
                if len(review_text.strip()) > 20:
                    reviews.append({
                        "title": None,
                        "rating": None,
                        "text": review_text.strip(),
                        "author": "Anonymous",
                        "verified_purchase": True
                    })
        
        # Log review findings
        if total_reviews:
            self.logger.info(f"✅ Total reviews: {total_reviews} | Scraped samples: {len(reviews)}")
            if len(reviews) < 10 and total_reviews >= 10:
                self.logger.warning(f"⚠ Only {len(reviews)} reviews scraped. Myntra loads reviews dynamically.")
        else:
            self.logger.info(f"Found {len(reviews)} reviews on product page")
        
        # If still no reviews, check if the page has a reviews section at all
        if len(reviews) == 0:
            reviews_section = response.css("[class*='review']").getall()
            self.logger.info(f"Reviews section HTML elements found: {len(reviews_section)}")
            if len(reviews_section) > 0:
                self.logger.info(f"Sample review HTML: {reviews_section[0][:200] if reviews_section else 'None'}")
        
        return {
            "title": title,
            "brand": brand,
            "price": price,
            "price_numeric": price_numeric,
            "original_price": original_price,
            "discount": discount,
            "availability": availability,
            "rating": float(rating) if rating else None,
            "total_reviews": total_reviews,
            "total_ratings": total_ratings,
            "images": images,
            "description": description,
            "specifications": specs,
            "sizes": sizes,
            "colors": colors,
            "reviews_from_page": reviews
        }

    def _extract_price(self, price_string):
        """Extract numeric price from string"""
        if not price_string:
            return None
        try:
            numeric_str = re.sub(r'[^\d.]', '', str(price_string))
            return float(numeric_str) if numeric_str else None
        except:
            return None

    def errback_handler(self, failure):
        self.logger.error(f"❌ Request failed: {failure}")
