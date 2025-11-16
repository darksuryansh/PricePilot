

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


class AmazonSpider(scrapy.Spider):
    name = "amazon"

    def __init__(self, url=None, api_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if url is None:
            raise ValueError("No URL provided. Use -a url=<your_url>")
        
        self.url = url
        
        # Get API key from command line argument or environment variable
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        
        # RapidAPI configuration (optional - only if api_key provided)
        if self.api_key:
            self.api_base_url = "https://amazon-data-scraper124.p.rapidapi.com"
            self.api_headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "amazon-data-scraper124.p.rapidapi.com"
            }
            self.logger.info("✓ API key loaded successfully")
        else:
            self.logger.warning("⚠ No API key provided - will skip API calls")
        
        self.human_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

    def start_requests(self):
        """Use Playwright for the initial request."""
        yield scrapy.Request(
            self.url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_context": "default",  # Changed from "persistent" to "default"
                "playwright_page_goto_kwargs": {
                    "wait_until": "networkidle",
                    "timeout": 60000,
                },
                "playwright_headers": {
                    "User-Agent": self.human_user_agent,
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                }
            },
            errback=self.errback_handler
        )

    def get_api_product_details(self, asin):
        """Get product details from RapidAPI"""
        if not self.api_key:
            return None
            
        url = f"{self.api_base_url}/products/{asin}"
        
        try:
            response = requests.get(url, headers=self.api_headers, timeout=90)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API product request failed: {e}")
            return None

    def get_api_reviews(self, asin):
        """Get reviews from RapidAPI"""
        if not self.api_key:
            return None
            
        url = f"{self.api_base_url}/products/{asin}/reviews"
        
        try:
            response = requests.get(url, headers=self.api_headers, timeout=90)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API reviews request failed: {e}")
            return None

    def parse(self, response):
        # Extract ASIN from URL
        asin_match = re.search(r"/dp/([A-Z0-9]{10})", self.url)
        asin = asin_match.group(1) if asin_match else None

        if not asin:
            self.logger.error("Could not extract ASIN from URL")
            return

        self.logger.info(f"Processing ASIN: {asin}")

        # --- SCRAPE FROM WEB PAGE ---
        scraped_data = self.scrape_from_page(response, asin)
        
        # --- GET DATA FROM API (if api_key provided) ---
        api_product_data = None
        api_reviews_data = None
        
        if self.api_key:
            self.logger.info("Fetching data from RapidAPI...")
            api_product_data = self.get_api_product_details(asin)
            api_reviews_data = self.get_api_reviews(asin)
        else:
            self.logger.info("No API key provided, skipping API calls")

        # --- COMBINE ALL DATA ---
        combined_data = {
            "asin": asin,
            "url": self.url,
            "platform": "amazon",  # Add platform identifier
            "title": scraped_data.get("title"),
            "brand": scraped_data.get("brand"),
            "price": scraped_data.get("price"),
            "availability": scraped_data.get("availability"),
            "rating": scraped_data.get("rating"),
            "total_reviews": scraped_data.get("total_reviews"),
            "images": scraped_data.get("images", []),
            "features": scraped_data.get("features", []),
            "description": scraped_data.get("description"),
            "specifications": scraped_data.get("specifications", {}),
            "categories": scraped_data.get("categories", []),
            "variations": scraped_data.get("variations", {}),
            "reviews_from_page": scraped_data.get("reviews_from_page", []),
            "api_product_data": api_product_data,
            "api_reviews_data": api_reviews_data,
        }

        yield combined_data

    def scrape_from_page(self, response, asin):
        """Scrape data directly from the Amazon product page"""
        
        # --- Product Information ---
        title = response.css("#productTitle::text").get()
        if title:
            title = title.strip()

        brand = (
            response.css("#bylineInfo::text").get() or
            response.css("#bylineInfo a::text").get() or
            response.css(".po-brand .po-break-word::text").get()
        )
        if brand:
            brand = brand.replace("Visit the", "").replace("Store", "").strip()

        price = (
            response.css(".a-price .a-offscreen::text").get() or
            response.css(".a-price-whole::text").get() or
            response.css("#corePrice_feature_div .a-offscreen::text").get()
        )

        availability = response.css("#availability span::text").get()
        if availability:
            availability = availability.strip()

        total_reviews = response.css("#acrCustomerReviewText::text").get()
        if total_reviews:
            total_reviews = total_reviews.strip()

        rating = (
            response.css("#acrPopover::attr(title)").get() or
            response.css(".a-icon-alt::text").re_first(r"([\d.]+) out of")
        )

        # --- Product Images ---
        images = []
        
        # Main product images with size info
        img_data = response.css("#imgTagWrapperId img::attr(data-a-dynamic-image)").get()
        if img_data:
            try:
                img_json = json.loads(img_data)
                # Sort by size (width * height) to get largest images first
                sorted_images = sorted(img_json.items(), key=lambda x: x[1][0] * x[1][1], reverse=True)
                images.extend([img[0] for img in sorted_images])
            except Exception:
                pass

        # Alternative image selectors - filter out small thumbnails
        alt_images = response.css("#altImages img::attr(src)").getall()
        # Filter out thumbnails (usually contain 'SS40', 'SS38', '_AC_US40_' in URL)
        large_images = [
            img for img in alt_images 
            if img and "https:" in img 
            and not any(thumb in img for thumb in ['SS40', 'SS38', 'SS50', '_AC_US40_', '_AC_UL40_'])
        ]
        # Upgrade image URLs to larger versions by replacing small size indicators
        for img in large_images:
            # Replace small sizes with larger ones
            img = img.replace('_AC_US40_', '_AC_SL1500_')
            img = img.replace('_AC_UL40_', '_AC_SL1500_')
            img = img.replace('_AC_US100_', '_AC_SL1500_')
            img = img.replace('._SS40_', '._SL1500_')
            if img not in images:
                images.append(img)

        # --- Product Features/Description ---
        features = []
        feature_bullets = response.css("#feature-bullets ul li span.a-list-item::text").getall()
        features = [f.strip() for f in feature_bullets if f.strip() and len(f.strip()) > 5]

        # Product description - try multiple selectors
        description = ""
        
        # Try productDescription section first
        description_parts = response.css("#productDescription p::text").getall()
        if description_parts:
            description = " ".join([d.strip() for d in description_parts if d.strip()])
            self.logger.info(f"✓ Found description in #productDescription p")
        
        # Try productDescription with all text nodes
        if not description:
            description_parts = response.css("#productDescription ::text").getall()
            if description_parts:
                # Filter out script/style content
                clean_parts = [d.strip() for d in description_parts 
                             if d.strip() and len(d.strip()) > 5 
                             and not d.strip().startswith('{') 
                             and not d.strip().startswith('.')
                             and 'function' not in d.strip().lower()
                             and 'display:' not in d.strip().lower()]
                description = " ".join(clean_parts)
                if description:
                    self.logger.info(f"✓ Found description in #productDescription")
        
        # Try book description
        if not description:
            book_desc = response.css("#bookDescription_feature_div noscript::text, #bookDescription_feature_div div::text").getall()
            if book_desc:
                description = " ".join([d.strip() for d in book_desc if d.strip()])
                if description:
                    self.logger.info(f"✓ Found description in bookDescription")
        
        # Try aplus content text only (Enhanced Brand Content) - more selective
        if not description:
            aplus_parts = response.css("#aplus p::text, #aplus .aplus-standard p::text, #aplus .apm-module-content ::text").getall()
            if aplus_parts:
                clean_parts = [d.strip() for d in aplus_parts 
                             if d.strip() and len(d.strip()) > 15 
                             and not d.strip().startswith('{') 
                             and not d.strip().startswith('.')
                             and 'function' not in d.strip().lower()
                             and 'background' not in d.strip().lower()
                             and 'width:' not in d.strip().lower()]
                description = " ".join(clean_parts)
                if description:
                    self.logger.info(f"✓ Found description in aplus content")
        
        # Try aplus-v2 content - more selective text extraction
        if not description:
            aplus_v2_parts = response.css("#aplus_feature_div p::text, #aplus_feature_div .apm-brand-story-text::text").getall()
            if aplus_v2_parts:
                clean_parts = [d.strip() for d in aplus_v2_parts 
                             if d.strip() and len(d.strip()) > 15
                             and not d.strip().startswith('{') 
                             and not d.strip().startswith('.')
                             and 'function' not in d.strip().lower()]
                description = " ".join(clean_parts)
                if description and len(description) > 50:  # Ensure substantial content
                    self.logger.info(f"✓ Found description in aplus_feature_div")
                else:
                    description = ""  # Reset if not substantial
        
        # Try product overview/details
        if not description:
            overview_parts = response.css(".product-facts-detail ::text, .apm-product-description ::text").getall()
            if overview_parts:
                description = " ".join([d.strip() for d in overview_parts if d.strip() and len(d.strip()) > 10])
                if description:
                    self.logger.info(f"✓ Found description in product overview")
        
        # As a last resort, use feature bullets as description if nothing else found
        if not description and features:
            description = " ".join(features[:3])  # Use first 3 features
            self.logger.info(f"✓ Using feature bullets as description (fallback)")
        
        # Clean up and limit description length
        if description:
            # Remove excessive whitespace
            description = " ".join(description.split())
            # Limit length to avoid too much data
            if len(description) > 2000:
                description = description[:2000] + "..."
            self.logger.info(f"✓ Final description length: {len(description)} characters")
        else:
            self.logger.warning("✗ No description found for product")

        # --- Product Details/Specifications ---
        specs = {}
        
        # Technical details table
        spec_rows = response.css("#prodDetails table tr, #productDetails_techSpec_section_1 tr")
        for row in spec_rows:
            key = row.css("th::text, td:first-child::text").get()
            value = row.css("td:last-child::text").get()
            if key and value:
                specs[key.strip()] = value.strip()

        # Additional product details
        detail_rows = response.css("#detailBullets_feature_div li")
        for row in detail_rows:
            full_text = row.css("::text").getall()
            full_text = " ".join([t.strip() for t in full_text if t.strip()])
            if ":" in full_text:
                parts = full_text.split(":", 1)
                if len(parts) == 2:
                    specs[parts[0].strip()] = parts[1].strip()

        # --- Customer Reviews from Page ---
        reviews = []
        review_elements = response.css('[data-hook="review"]')
        
        self.logger.info(f"Found {len(review_elements)} reviews on product page")
        
        for review in review_elements:
            review_title = review.css('[data-hook="review-title"] span::text').getall()
            title_text = review_title[-1].strip() if review_title else None
            
            rating_elem = review.css('[data-hook="review-star-rating"] span::text').get()
            
            text_parts = review.css('[data-hook="review-body"] span::text').getall()
            text = " ".join([t.strip() for t in text_parts if t.strip()]) if text_parts else None
            
            author = review.css('.a-profile-name::text').get()
            date = review.css('[data-hook="review-date"]::text').get()
            
            helpful_count = review.css('[data-hook="helpful-vote-statement"]::text').get()
            
            verified = "Verified Purchase" in review.get()
            
            if text:
                reviews.append({
                    "title": title_text,
                    "rating": rating_elem.strip() if rating_elem else None,
                    "text": text,
                    "author": author.strip() if author else None,
                    "date": date.strip() if date else None,
                    "helpful_count": helpful_count,
                    "verified_purchase": verified
                })

        # --- Categories/breadcrumbs ---
        categories = response.css("#wayfinding-breadcrumbs_feature_div li a::text").getall()
        categories = [cat.strip() for cat in categories if cat.strip()]

        # --- Product Variations ---
        variations = {}
        variation_elements = response.css("#variation_size_name ul li, .twisterSwatchWrapper")
        for var in variation_elements:
            var_text = var.css("::text").get()
            if var_text:
                variations[var_text.strip()] = True

        return {
            "title": title,
            "brand": brand,
            "price": price,
            "availability": availability,
            "total_reviews": total_reviews,
            "rating": rating,
            "images": list(set(images)),  # Remove duplicates
            "features": features,
            "description": description,
            "specifications": specs,
            "categories": categories,
            "variations": variations,
            "reviews_from_page": reviews
        }

    def errback_handler(self, failure):
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")


# scrapy crawl amazon -a url="https://www.amazon.in/Kitchen-Manufacturer-Warranty-capacity-SF400/dp/B083C6XMKQ" -a api_key="24356f5fddmsh6afec693b34efc7p1a8ebejsn06df89b3fe15" -o amazon.json


#scrapy crawl amazon \ -a url="https://www.amazon.in/Kitchen-Manufacturer-Warranty-capacity-SF400/dp/B083C6XMKQ" \-a api_key="24356f5fddmsh6afec693b34efc7p1a8ebejsn06df89b3fe15"