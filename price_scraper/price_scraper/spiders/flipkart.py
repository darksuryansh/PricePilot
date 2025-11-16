# # # scrapy crawl flipkart -a url="https://www.flipkart.com/..." -o flipkart.json





# import re
# import json
# import os
# import scrapy
# from dotenv import load_dotenv
# from pathlib import Path
# from scrapy_playwright.page import PageMethod

# # Load environment variables
# env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
# load_dotenv(dotenv_path=env_path)


# class FlipkartSpider(scrapy.Spider):
#     name = "flipkart"

#     def __init__(self, url=None, product_id=None, api_key=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         self.url = url
#         self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        
#         if url and not product_id:
#             product_id_match = re.search(r"pid=([A-Z0-9]+)", url)
#             self.product_id = product_id_match.group(1) if product_id_match else None
#         else:
#             self.product_id = product_id
        
#         if not url and not product_id:
#             raise ValueError("Either URL or product_id must be provided")

#     def start_requests(self):
#         """Start scraping with aggressive review loading"""
        
#         if self.url:
#             yield scrapy.Request(
#                 self.url,
#                 callback=self.parse_product,
#                 dont_filter=True,
#                 meta={
#                     "playwright": True,
#                     "playwright_context": "default",
#                     "playwright_page_goto_kwargs": {
#                         "wait_until": "networkidle",
#                         "timeout": 60000,
#                     },
#                     "playwright_page_methods": [
#                         # Wait for page load
#                         PageMethod("wait_for_timeout", 3000),
                        
#                         # Scroll to bottom slowly (loads more content)
#                         PageMethod("evaluate", """
#                             async () => {
#                                 for (let i = 0; i < 10; i++) {
#                                     window.scrollBy(0, 300);
#                                     await new Promise(r => setTimeout(r, 300));
#                                 }
#                             }
#                         """),
#                         PageMethod("wait_for_timeout", 2000),
                        
#                         # Try to click "View All Reviews" or "Read More Reviews"
#                         PageMethod("evaluate", """
#                             () => {
#                                 // Try multiple button selectors
#                                 const buttons = [
#                                     ...document.querySelectorAll('div._2aV-V4'),
#                                     ...document.querySelectorAll('span._2-N8zT'),
#                                     ...document.querySelectorAll('div._3UAT2v'),
#                                     ...document.querySelectorAll('a[href*="reviews"]'),
#                                 ];
#                                 buttons.forEach(btn => {
#                                     if (btn && btn.textContent.includes('All Reviews')) {
#                                         btn.click();
#                                     }
#                                 });
#                             }
#                         """),
#                         PageMethod("wait_for_timeout", 3000),
                        
#                         # Scroll reviews section multiple times
#                         PageMethod("evaluate", """
#                             async () => {
#                                 const reviewSection = document.querySelector('div.col.JOpGWq');
#                                 if (reviewSection) {
#                                     for (let i = 0; i < 5; i++) {
#                                         reviewSection.scrollTop += 500;
#                                         await new Promise(r => setTimeout(r, 500));
#                                     }
#                                 }
#                             }
#                         """),
#                         PageMethod("wait_for_timeout", 2000),
#                     ],
#                 },
#                 errback=self.errback_handler
#             )

#     def parse_product(self, response):
#         """Parse product page"""
        
#         product_id_match = re.search(r"pid=([A-Z0-9]+)", self.url)
#         product_id = product_id_match.group(1) if product_id_match else None

#         if not product_id:
#             self.logger.error("❌ Could not extract product ID")
#             return

#         self.logger.info(f"✅ Processing product: {product_id}")

#         # Scrape all data
#         scraped_data = self.scrape_from_page(response, product_id)
        
#         combined_data = {
#             "product_id": product_id,
#             "url": self.url,
#             "title": scraped_data.get("title"),
#             "brand": scraped_data.get("brand"),
#             "price": scraped_data.get("price"),
#             "price_numeric": scraped_data.get("price_numeric"),
#             "availability": scraped_data.get("availability"),
#             "rating": scraped_data.get("rating"),
#             "total_reviews": scraped_data.get("total_reviews"),
#             "total_ratings": scraped_data.get("total_ratings"),
#             "images": scraped_data.get("images", []),
#             "highlights": scraped_data.get("highlights", []),
#             "description": scraped_data.get("description"),
#             "specifications": scraped_data.get("specifications", {}),
#             "reviews_from_page": scraped_data.get("reviews_from_page", []),
#             "data_source": "web_scraping"
#         }

#         yield combined_data

#     def scrape_from_page(self, response, product_id):
#         """Scrape product data from page"""
        
#         ld_json_data = self.extract_json_ld(response)
        
#         # Title
#         title = (
#             ld_json_data.get("name") or
#             response.css("span.B_NuCI::text, span.VU-ZEz::text, h1.yhB1nd::text").get()
#         )
#         if title:
#             title = title.strip()

#         # Brand
#         brand = None
#         if ld_json_data.get("brand"):
#             brand = ld_json_data["brand"].get("name")
#         if not brand:
#             brand = response.css("a._2rpwqI::text").get()
#         if not brand and title:
#             brand = title.split()[0]

#         # Price
#         price = None
#         if ld_json_data.get("offers"):
#             price = ld_json_data["offers"].get("price")
#         if not price:
#             price = response.css("div._30jeq3._16Jk6d::text, div._30jeq3::text").get()
#         price_numeric = self._extract_price(price)

#         # Availability
#         availability = "In Stock"
#         if response.css("div._16FRp0").get():
#             availability = "Out of Stock"

#         # Rating & Reviews
#         rating = None
#         if ld_json_data.get("aggregateRating"):
#             rating = ld_json_data["aggregateRating"].get("ratingValue")
#         if not rating:
#             rating = response.css("div._3LWZlK::text, div._3i9cqz::text").get()
        
#         total_reviews = None
#         total_ratings = None
#         reviews_text = response.css('span._2_R_DZ::text, span._13vcmD::text').get()
#         if reviews_text:
#             ratings_match = re.search(r'([\d,]+)\s+Ratings?', reviews_text)
#             reviews_match = re.search(r'([\d,]+)\s+Reviews?', reviews_text)
#             if ratings_match:
#                 total_ratings = int(ratings_match.group(1).replace(',', ''))
#             if reviews_match:
#                 total_reviews = int(reviews_match.group(1).replace(',', ''))

#         # FIXED: Get CORRECT product images only
#         images = self.extract_product_images(response, ld_json_data)
#         self.logger.info(f"✅ Extracted {len(images)} product images")

#         # Highlights
#         highlights = response.css("ul._1_Y6L > li::text, div._1xgFc9 li::text").getall()
#         highlights = [h.strip() for h in highlights if h.strip()]

#         # Description
#         description_parts = response.css("div._1mXcCf p::text, div._3WHvuP::text").getall()
#         description = " ".join([d.strip() for d in description_parts if d.strip()])

#         # Specifications
#         specs = {}
#         spec_selectors = [
#             "table._14cfVK tr",
#             "div._2418kt table tr",
#             "table.IwbwGp tr",
#         ]
        
#         for spec_selector in spec_selectors:
#             spec_rows = response.css(spec_selector)
#             if spec_rows:
#                 for row in spec_rows:
#                     key = row.css("td:first-child::text, th::text").get()
#                     value = row.css("td:last-child::text, td:nth-child(2)::text").get()
#                     if key and value:
#                         specs[key.strip()] = value.strip()
#                 if specs:
#                     break

#         # FIXED: Extract ALL reviews
#         reviews = self.extract_all_reviews(response)
#         self.logger.info(f"✅ Extracted {len(reviews)} total reviews")

#         return {
#             "title": title,
#             "brand": brand,
#             "price": price,
#             "price_numeric": price_numeric,
#             "availability": availability,
#             "rating": float(rating) if rating else None,
#             "total_reviews": total_reviews,
#             "total_ratings": total_ratings,
#             "images": images,
#             "highlights": highlights,
#             "description": description,
#             "specifications": specs,
#             "reviews_from_page": reviews
#         }

#     def extract_product_images(self, response, ld_json_data):
#         """Extract ONLY product images (not random ads/banners)"""
        
#         images = []
        
#         # Method 1: From JSON-LD (most reliable)
#         if ld_json_data.get("image"):
#             if isinstance(ld_json_data["image"], list):
#                 images.extend(ld_json_data["image"])
#             else:
#                 images.append(ld_json_data["image"])
            
#             # Clean and validate
#             images = [img for img in images if img and 'http' in img]
#             if images:
#                 self.logger.info(f"Got {len(images)} images from JSON-LD")
#                 return images[:10]  # Limit to 10 images
        
#         # Method 2: Product image gallery (left side thumbnails + main image)
#         image_gallery = response.css("div._1AtVbE img::attr(src), div._3li7GG img::attr(src)").getall()
        
#         if image_gallery:
#             # Filter out small icons/logos
#             images = [
#                 img for img in image_gallery 
#                 if img and ('http' in img or img.startswith('//'))
#                 and 'rukmini' in img.lower()  # Flipkart product images are on rukmini CDN
#                 and '128/128' not in img  # Exclude small thumbnails
#                 and '200/200' not in img
#             ]
            
#             # Convert protocol-relative URLs
#             images = ['https:' + img if img.startswith('//') else img for img in images]
            
#             # Upgrade to higher resolution
#             images = [re.sub(r'/\d{3,4}/\d{3,4}/', '/832/832/', img) for img in images]
            
#             # Remove duplicates while preserving order
#             seen = set()
#             unique_images = []
#             for img in images:
#                 if img not in seen:
#                     seen.add(img)
#                     unique_images.append(img)
            
#             if unique_images:
#                 self.logger.info(f"Got {len(unique_images)} images from gallery")
#                 return unique_images[:10]
        
#         # Method 3: Main product image only (fallback)
#         main_image = response.css("img._396cs4::attr(src), img._2r_T1I::attr(src)").get()
#         if main_image:
#             if main_image.startswith('//'):
#                 main_image = 'https:' + main_image
#             # Upgrade resolution
#             main_image = re.sub(r'/\d{3,4}/\d{3,4}/', '/832/832/', main_image)
#             self.logger.info("Got 1 main product image")
#             return [main_image]
        
#         self.logger.warning("⚠️ No product images found")
#         return []

#     def extract_all_reviews(self, response):
#         """Extract ALL reviews from the page"""
        
#         reviews = []
        
#         # Try to find the main reviews container
#         # Flipkart has multiple layouts, try all
#         review_selectors = [
#             "div.col._2wzgFH",  # Standard review card
#             "div.cPHDOP.col-12-12",  # Alternative layout
#             "div._1AtVbE.col-12-12",  # Another variant
#             "div.t-ZTKy",  # Review text container
#         ]
        
#         review_containers = []
#         for selector in review_selectors:
#             containers = response.css(selector)
#             if len(containers) >= 1:
#                 review_containers = containers
#                 self.logger.info(f"✓ Found {len(containers)} reviews using: {selector}")
#                 break
        
#         if not review_containers:
#             self.logger.warning("⚠️ No review containers found")
#             return reviews
        
#         # Process each review
#         for idx, review in enumerate(review_containers, 1):
#             # Extract all data
#             title = review.css("p._2-N8zT::text, p._2xg6Ul::text, p.z9E0IG::text").get()
#             rating = review.css("div._3LWZlK::text, div._1i0wk8::text").get()
            
#             # Get review text (try multiple selectors)
#             text = None
#             for text_selector in [
#                 "div.t-ZTKy div::text",
#                 "div._3nrCtb::text",
#                 "div.ZmyHeo div::text",
#                 "div.qwjRop div::text"
#             ]:
#                 text_parts = review.css(text_selector).getall()
#                 if text_parts:
#                     text = " ".join([t.strip() for t in text_parts if t.strip() and len(t.strip()) > 3])
#                     if text and len(text) > 20:
#                         break
            
#             author = review.css("p._2sc7ZR::text, p._2NsDsF::text").get()
#             date = review.css("p._2mcZGG::text, p._2NsDsF.jhIwwS::text").get()
#             verified = bool(review.css("div._1_BQL8::text, span._2N5RGd::text").get())
            
#             # Validate review
#             if text and len(text) > 25:
#                 # Skip UI elements
#                 skip_patterns = [
#                     'secure delivery', 'available offers', 'enter pincode',
#                     'min. 50% off', 'questions and answers', 'similar products'
#                 ]
                
#                 text_lower = text.lower()
#                 is_ui_element = any(pattern in text_lower for pattern in skip_patterns)
#                 starts_with_price = text.strip().startswith('₹')
                
#                 if not is_ui_element and not starts_with_price:
#                     reviews.append({
#                         "title": title.strip() if title else None,
#                         "rating": rating.strip() if rating else None,
#                         "text": text.strip()[:500],  # Limit to 500 chars
#                         "author": author.strip() if author else "Anonymous",
#                         "date": date.strip() if date else None,
#                         "verified_purchase": verified
#                     })
#                     self.logger.info(f"✓ Review {len(reviews)}: {text[:50]}...")
        
#         return reviews

#     def extract_json_ld(self, response):
#         """Extract JSON-LD structured data"""
#         ld_json_text = response.xpath('//script[@type="application/ld+json"]/text()').get()
#         if not ld_json_text:
#             return {}
#         try:
#             loaded = json.loads(ld_json_text)
#             if isinstance(loaded, list):
#                 return next((item for item in loaded if item.get('@type') == 'Product'), {})
#             return loaded if loaded.get('@type') == 'Product' else {}
#         except:
#             return {}

#     def _extract_price(self, price_string):
#         """Extract numeric price from string"""
#         if not price_string:
#             return None
#         try:
#             numeric_str = re.sub(r'[^\d.]', '', str(price_string))
#             return float(numeric_str) if numeric_str else None
#         except:
#             return None

#     def errback_handler(self, failure):
#         self.logger.error(f"❌ Request failed: {failure}")











# price_scraper/spiders/flipkart.py

# import re
# import json
# import os
# import scrapy
# from dotenv import load_dotenv
# from pathlib import Path
# from scrapy_playwright.page import PageMethod

# # Load environment variables
# env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
# load_dotenv(dotenv_path=env_path)


# class FlipkartSpider(scrapy.Spider):
#     name = "flipkart"

#     def __init__(self, url=None, product_id=None, api_key=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         self.url = url
#         self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        
#         if url and not product_id:
#             product_id_match = re.search(r"pid=([A-Z0-9]+)", url)
#             self.product_id = product_id_match.group(1) if product_id_match else None
#         else:
#             self.product_id = product_id
        
#         if not url and not product_id:
#             raise ValueError("Either URL or product_id must be provided")

#     def start_requests(self):
#         """Start scraping with aggressive review loading"""
        
#         if self.url:
#             yield scrapy.Request(
#                 self.url,
#                 callback=self.parse_product,
#                 dont_filter=True,
#                 meta={
#                     "playwright": True,
#                     "playwright_context": "default",
#                     "playwright_page_goto_kwargs": {
#                         "wait_until": "networkidle",
#                         "timeout": 60000,
#                     },
#                     "playwright_page_methods": [
#                         # Wait for initial load
#                         PageMethod("wait_for_timeout", 3000),
                        
#                         # Scroll slowly to load all content
#                         PageMethod("evaluate", """
#                             async () => {
#                                 for (let i = 0; i < 10; i++) {
#                                     window.scrollBy(0, 300);
#                                     await new Promise(r => setTimeout(r, 300));
#                                 }
#                             }
#                         """),
#                         PageMethod("wait_for_timeout", 2000),
                        
#                         # Try to click "View All Reviews" button
#                         PageMethod("evaluate", """
#                             () => {
#                                 const buttons = [
#                                     ...document.querySelectorAll('div._2aV-V4'),
#                                     ...document.querySelectorAll('span._2-N8zT'),
#                                     ...document.querySelectorAll('div._3UAT2v'),
#                                 ];
#                                 buttons.forEach(btn => {
#                                     if (btn && btn.textContent.includes('All Reviews')) {
#                                         btn.click();
#                                     }
#                                 });
#                             }
#                         """),
#                         PageMethod("wait_for_timeout", 3000),
                        
#                         # Scroll reviews section
#                         PageMethod("evaluate", """
#                             async () => {
#                                 const reviewSection = document.querySelector('div.col.JOpGWq');
#                                 if (reviewSection) {
#                                     for (let i = 0; i < 5; i++) {
#                                         reviewSection.scrollTop += 500;
#                                         await new Promise(r => setTimeout(r, 500));
#                                     }
#                                 }
#                             }
#                         """),
#                         PageMethod("wait_for_timeout", 2000),
#                     ],
#                 },
#                 errback=self.errback_handler
#             )

#     def parse_product(self, response):
#         """Parse product page"""
        
#         # Save HTML for debugging (optional - comment out in production)
#         # with open('debug_flipkart.html', 'w', encoding='utf-8') as f:
#         #     f.write(response.text)
#         # self.logger.info("✓ Saved HTML to debug_flipkart.html")
        
#         product_id_match = re.search(r"pid=([A-Z0-9]+)", self.url)
#         product_id = product_id_match.group(1) if product_id_match else None

#         if not product_id:
#             self.logger.error("❌ Could not extract product ID")
#             return

#         self.logger.info(f"✅ Processing product: {product_id}")

#         # Scrape all data
#         scraped_data = self.scrape_from_page(response, product_id)
        
#         combined_data = {
#             "product_id": product_id,
#             "url": self.url,
#             "title": scraped_data.get("title"),
#             "brand": scraped_data.get("brand"),
#             "price": scraped_data.get("price"),
#             "price_numeric": scraped_data.get("price_numeric"),
#             "availability": scraped_data.get("availability"),
#             "rating": scraped_data.get("rating"),
#             "total_reviews": scraped_data.get("total_reviews"),
#             "total_ratings": scraped_data.get("total_ratings"),
#             "images": scraped_data.get("images", []),
#             "highlights": scraped_data.get("highlights", []),
#             "description": scraped_data.get("description"),
#             "specifications": scraped_data.get("specifications", {}),
#             "reviews_from_page": scraped_data.get("reviews_from_page", []),
#             "data_source": "web_scraping"
#         }

#         yield combined_data

#     def scrape_from_page(self, response, product_id):
#         """Scrape product data from page"""
        
#         ld_json_data = self.extract_json_ld(response)
        
#         # Title
#         title = (
#             ld_json_data.get("name") or
#             response.css("span.B_NuCI::text, span.VU-ZEz::text, h1.yhB1nd::text").get()
#         )
#         if title:
#             title = title.strip()

#         # Brand
#         brand = None
#         if ld_json_data.get("brand"):
#             brand = ld_json_data["brand"].get("name")
#         if not brand:
#             brand = response.css("a._2rpwqI::text").get()
#         if not brand and title:
#             brand = title.split()[0]

#         # Price
#         price = None
#         if ld_json_data.get("offers"):
#             price = ld_json_data["offers"].get("price")
#         if not price:
#             price = response.css("div._30jeq3._16Jk6d::text, div._30jeq3::text").get()
#         price_numeric = self._extract_price(price)

#         # Availability
#         availability = "In Stock"
#         if response.css("div._16FRp0").get():
#             availability = "Out of Stock"

#         # Rating & Reviews
#         rating = None
#         if ld_json_data.get("aggregateRating"):
#             rating = ld_json_data["aggregateRating"].get("ratingValue")
#         if not rating:
#             rating = response.css("div._3LWZlK::text, div._3i9cqz::text").get()
        
#         total_reviews = None
#         total_ratings = None
#         reviews_text = response.css('span._2_R_DZ::text, span._13vcmD::text').get()
#         if reviews_text:
#             ratings_match = re.search(r'([\d,]+)\s+Ratings?', reviews_text)
#             reviews_match = re.search(r'([\d,]+)\s+Reviews?', reviews_text)
#             if ratings_match:
#                 total_ratings = int(ratings_match.group(1).replace(',', ''))
#             if reviews_match:
#                 total_reviews = int(reviews_match.group(1).replace(',', ''))

#         # FIXED: Get correct product images
#         images = self.extract_product_images(response, ld_json_data)
#         self.logger.info(f"✅ Extracted {len(images)} product images")

#         # Highlights
#         highlights = response.css("ul._1_Y6L > li::text, div._1xgFc9 li::text").getall()
#         highlights = [h.strip() for h in highlights if h.strip()]

#         # Description
#         description_parts = response.css("div._1mXcCf p::text, div._3WHvuP::text").getall()
#         description = " ".join([d.strip() for d in description_parts if d.strip()])

#         # Specifications
#         specs = {}
#         spec_selectors = [
#             "table._14cfVK tr",
#             "div._2418kt table tr",
#             "table.IwbwGp tr",
#         ]
        
#         for spec_selector in spec_selectors:
#             spec_rows = response.css(spec_selector)
#             if spec_rows:
#                 for row in spec_rows:
#                     key = row.css("td:first-child::text, th::text").get()
#                     value = row.css("td:last-child::text, td:nth-child(2)::text").get()
#                     if key and value:
#                         specs[key.strip()] = value.strip()
#                 if specs:
#                     break

#         # FIXED: Extract ALL reviews
#         reviews = self.extract_all_reviews(response)

#         return {
#             "title": title,
#             "brand": brand,
#             "price": price,
#             "price_numeric": price_numeric,
#             "availability": availability,
#             "rating": float(rating) if rating else None,
#             "total_reviews": total_reviews,
#             "total_ratings": total_ratings,
#             "images": images,
#             "highlights": highlights,
#             "description": description,
#             "specifications": specs,
#             "reviews_from_page": reviews
#         }

#     def extract_product_images(self, response, ld_json_data):
#         """Extract ONLY product images (not ads/banners)"""
        
#         images = []
        
#         # Method 1: JSON-LD (most reliable)
#         if ld_json_data.get("image"):
#             if isinstance(ld_json_data["image"], list):
#                 images.extend(ld_json_data["image"])
#             else:
#                 images.append(ld_json_data["image"])
            
#             images = [img for img in images if img and 'http' in img]
#             if images:
#                 self.logger.info(f"Got {len(images)} images from JSON-LD")
#                 return images[:10]
        
#         # Method 2: Image gallery
#         image_gallery = response.css("div._1AtVbE img::attr(src), div._3li7GG img::attr(src)").getall()
        
#         if image_gallery:
#             images = [
#                 img for img in image_gallery 
#                 if img and ('http' in img or img.startswith('//'))
#                 and 'rukmini' in img.lower()
#                 and '128/128' not in img
#                 and '200/200' not in img
#             ]
            
#             images = ['https:' + img if img.startswith('//') else img for img in images]
#             images = [re.sub(r'/\d{3,4}/\d{3,4}/', '/832/832/', img) for img in images]
            
#             seen = set()
#             unique_images = []
#             for img in images:
#                 if img not in seen:
#                     seen.add(img)
#                     unique_images.append(img)
            
#             if unique_images:
#                 self.logger.info(f"Got {len(unique_images)} images from gallery")
#                 return unique_images[:10]
        
#         # Method 3: Main image
#         main_image = response.css("img._396cs4::attr(src), img._2r_T1I::attr(src)").get()
#         if main_image:
#             if main_image.startswith('//'):
#                 main_image = 'https:' + main_image
#             main_image = re.sub(r'/\d{3,4}/\d{3,4}/', '/832/832/', main_image)
#             self.logger.info("Got 1 main product image")
#             return [main_image]
        
#         self.logger.warning("⚠️ No product images found")
#         return []

#     def extract_all_reviews(self, response):
#         """Extract ALL real reviews with detailed logging"""
        
#         reviews = []
        
#         self.logger.info("=" * 60)
#         self.logger.info("STARTING REVIEW EXTRACTION")
#         self.logger.info("=" * 60)
        
#         # Try multiple selectors
#         review_selectors = [
#             ("div.col._2wzgFH", "main review cards"),
#             ("div.cPHDOP.col-12-12", "alternative cards"),
#             ("div._1AtVbE.col-12-12", "backup cards"),
#         ]
        
#         review_containers = []
#         used_selector = None
        
#         for selector, desc in review_selectors:
#             containers = response.css(selector)
#             if len(containers) >= 1:
#                 review_containers = containers
#                 used_selector = selector
#                 self.logger.info(f"✓ Using selector: {selector}")
#                 self.logger.info(f"✓ Found {len(containers)} total containers")
#                 break
        
#         if not review_containers:
#             self.logger.error("❌ No review containers found!")
#             return reviews
        
#         # Process each container
#         for idx, container in enumerate(review_containers, 1):
#             self.logger.info(f"\n--- Container {idx}/{len(review_containers)} ---")
            
#             # Extract review text
#             review_text = None
            
#             text_selectors = [
#                 "div.t-ZTKy div",
#                 "div._3nrCtb",
#                 "div.ZmyHeo div",
#                 "div.qwjRop div",
#             ]
            
#             for text_sel in text_selectors:
#                 text_elements = container.css(f"{text_sel}::text").getall()
#                 if text_elements:
#                     review_text = " ".join([
#                         t.strip() 
#                         for t in text_elements 
#                         if t.strip() and len(t.strip()) > 5
#                     ])
                    
#                     if review_text and len(review_text) > 30:
#                         self.logger.info(f"  ✓ Text found with: {text_sel}")
#                         break
            
#             # Fallback: get all text
#             if not review_text or len(review_text) < 30:
#                 all_text = container.css("::text").getall()
#                 review_text = " ".join([
#                     t.strip() 
#                     for t in all_text 
#                     if t.strip() and len(t.strip()) > 5 and not t.strip().startswith('₹')
#                 ])
            
#             # Skip if no valid text
#             if not review_text or len(review_text) < 30:
#                 self.logger.warning(f"  ⚠ No valid text (len={len(review_text or '')})")
#                 continue
            
#             # Validation
#             skip_keywords = [
#                 'secure delivery', 'available offers', 'enter pincode',
#                 'questions and answers', 'min. 50% off', 'safe and secure',
#                 'similar products', 'you might also like', 'buy now',
#                 'add to cart', 'view details', 'specifications'
#             ]
            
#             text_lower = review_text.lower()
#             is_ui = any(kw in text_lower for kw in skip_keywords)
#             starts_rupee = review_text.strip().startswith('₹')
#             too_short = len(review_text) < 30
#             too_long = len(review_text) > 1000
            
#             if is_ui:
#                 self.logger.warning(f"  ✗ Skipped: UI element")
#                 continue
#             if starts_rupee:
#                 self.logger.warning(f"  ✗ Skipped: Price string")
#                 continue
#             if too_long:
#                 self.logger.warning(f"  ✗ Skipped: Too long ({len(review_text)} chars)")
#                 continue
            
#             # Extract metadata
#             title = container.css("p._2-N8zT::text, p._2xg6Ul::text").get()
#             rating = container.css("div._3LWZlK::text, div._1i0wk8::text").get()
#             author = container.css("p._2sc7ZR::text, p._2NsDsF::text").get()
#             date = container.css("p._2mcZGG::text").get()
#             verified = bool(container.css("div._1_BQL8::text").get())
            
#             review_dict = {
#                 "title": title.strip() if title else None,
#                 "rating": rating.strip() if rating else None,
#                 "text": review_text.strip()[:500],
#                 "author": author.strip() if author else "Anonymous",
#                 "date": date.strip() if date else None,
#                 "verified_purchase": verified
#             }
            
#             reviews.append(review_dict)
#             self.logger.info(f"  ✅ REVIEW {len(reviews)} ADDED")
#             self.logger.info(f"  Text: {review_text[:60]}...")
        
#         self.logger.info("=" * 60)
#         self.logger.info(f"✅ EXTRACTED {len(reviews)} valid reviews from {len(review_containers)} containers")
#         self.logger.info("=" * 60)
        
#         return reviews

#     def extract_json_ld(self, response):
#         """Extract JSON-LD structured data"""
#         ld_json_text = response.xpath('//script[@type="application/ld+json"]/text()').get()
#         if not ld_json_text:
#             return {}
#         try:
#             loaded = json.loads(ld_json_text)
#             if isinstance(loaded, list):
#                 return next((item for item in loaded if item.get('@type') == 'Product'), {})
#             return loaded if loaded.get('@type') == 'Product' else {}
#         except:
#             return {}

#     def _extract_price(self, price_string):
#         """Extract numeric price from string"""
#         if not price_string:
#             return None
#         try:
#             numeric_str = re.sub(r'[^\d.]', '', str(price_string))
#             return float(numeric_str) if numeric_str else None
#         except:
#             return None

#     def errback_handler(self, failure):
#         self.logger.error(f"❌ Request failed: {failure}")








# price_scraper/spiders/flipkart.py

import re
import json
import os
import scrapy
from dotenv import load_dotenv
from pathlib import Path
from scrapy_playwright.page import PageMethod

env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class FlipkartSpider(scrapy.Spider):
    name = "flipkart"

    def __init__(self, url=None, product_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        
        if url and not product_id:
            product_id_match = re.search(r"pid=([A-Z0-9]+)", url)
            self.product_id = product_id_match.group(1) if product_id_match else None
        else:
            self.product_id = product_id
        
        if not url and not product_id:
            raise ValueError("Either URL or product_id must be provided")

    def start_requests(self):
        """Enhanced review loading strategy - aiming for 10-20 reviews"""
        
        if self.url:
            yield scrapy.Request(
                self.url,
                callback=self.parse_product,
                dont_filter=True,
                meta={
                    "playwright": True,
                    "playwright_context": "default",
                    "playwright_page_goto_kwargs": {
                        "wait_until": "domcontentloaded",
                        "timeout": 60000,
                    },
                    "playwright_page_methods": [
                        # Wait for initial load
                        PageMethod("wait_for_timeout", 3000),
                        
                        # Scroll down page slowly to trigger lazy loading
                        PageMethod("evaluate", """
                            async () => {
                                for (let i = 0; i < 15; i++) {
                                    window.scrollBy(0, 350);
                                    await new Promise(r => setTimeout(r, 350));
                                }
                            }
                        """),
                        PageMethod("wait_for_timeout", 2000),
                        
                        # Scroll back up to reviews section and scroll it internally
                        PageMethod("evaluate", """
                            async () => {
                                const reviewSection = document.querySelector('div.col.JOpGWq, div.col.pPAw9M');
                                if (reviewSection) {
                                    reviewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                    await new Promise(r => setTimeout(r, 1500));
                                    
                                    // Scroll within the reviews container to load more
                                    for (let i = 0; i < 10; i++) {
                                        reviewSection.scrollTop += 450;
                                        await new Promise(r => setTimeout(r, 450));
                                    }
                                }
                            }
                        """),
                        PageMethod("wait_for_timeout", 2500),
                        
                        # Final scroll of entire page
                        PageMethod("evaluate", """
                            async () => {
                                for (let i = 0; i < 8; i++) {
                                    window.scrollBy(0, 400);
                                    await new Promise(r => setTimeout(r, 300));
                                }
                            }
                        """),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                },
                errback=self.errback_handler
            )

    def parse_product(self, response):
        """Parse product page"""
        
        product_id_match = re.search(r"pid=([A-Z0-9]+)", self.url)
        product_id = product_id_match.group(1) if product_id_match else None

        if not product_id:
            self.logger.error("❌ Could not extract product ID")
            return

        self.logger.info(f"✅ Processing product: {product_id}")

        # Scrape data
        scraped_data = self.scrape_from_page(response, product_id)
        
        combined_data = {
            "product_id": product_id,
            "url": self.url,
            "platform": "flipkart",  # Add platform identifier
            "title": scraped_data.get("title"),
            "brand": scraped_data.get("brand"),
            "price": scraped_data.get("price"),
            "price_numeric": scraped_data.get("price_numeric"),
            "availability": scraped_data.get("availability"),
            "rating": scraped_data.get("rating"),
            "total_reviews": scraped_data.get("total_reviews"),
            "total_ratings": scraped_data.get("total_ratings"),
            "images": scraped_data.get("images", []),
            "highlights": scraped_data.get("highlights", []),
            "description": scraped_data.get("description"),
            "specifications": scraped_data.get("specifications", {}),
            "reviews_from_page": scraped_data.get("reviews_from_page", []),
            "data_source": "web_scraping"
        }

        yield combined_data

    def scrape_from_page(self, response, product_id):
        """Scrape product data"""
        
        ld_json_data = self.extract_json_ld(response)
        
        # Title
        title = (
            ld_json_data.get("name") or
            response.css("span.B_NuCI::text, span.VU-ZEz::text, h1.yhB1nd::text").get()
        )
        if title:
            title = title.strip()

        # Brand
        brand = None
        if ld_json_data.get("brand"):
            brand = ld_json_data["brand"].get("name")
        if not brand:
            brand = response.css("a._2rpwqI::text").get()
        if not brand and title:
            brand = title.split()[0]

        # Price
        price = None
        if ld_json_data.get("offers"):
            price = ld_json_data["offers"].get("price")
        if not price:
            price = response.css("div._30jeq3._16Jk6d::text, div._30jeq3::text").get()
        price_numeric = self._extract_price(price)

        # Availability
        availability = "In Stock"
        if response.css("div._16FRp0").get():
            availability = "Out of Stock"

        # Rating
        rating = None
        if ld_json_data.get("aggregateRating"):
            rating = ld_json_data["aggregateRating"].get("ratingValue")
        if not rating:
            # Try multiple selectors
            rating = response.css("div._3LWZlK::text, div._3i9cqz::text, div.XQDdHH::text").get()
        
        # Reviews count - UPDATED SELECTORS (Nov 2025)
        total_reviews = None
        total_ratings = None
        
        # Method 1: From the main product rating section (more specific)
        rating_section = response.css('div._5OesEi.HDvrBb span.Wphh3N')
        if rating_section:
            reviews_text = rating_section.css('::text').getall()
            reviews_text_combined = " ".join(reviews_text)
            
            if reviews_text_combined:
                ratings_match = re.search(r'([\d,]+)\s+Ratings?', reviews_text_combined)
                reviews_match = re.search(r'([\d,]+)\s+Reviews?', reviews_text_combined)
                if ratings_match:
                    total_ratings = int(ratings_match.group(1).replace(',', ''))
                if reviews_match:
                    total_reviews = int(reviews_match.group(1).replace(',', ''))
        
        # Method 2: Fallback - try from reviews section
        if not total_reviews or not total_ratings:
            reviews_section_text = response.css('div.row.j-aW8Z span::text').getall()
            reviews_text_combined = " ".join(reviews_section_text)
            
            if reviews_text_combined:
                ratings_match = re.search(r'([\d,]+)\s+Ratings?', reviews_text_combined)
                reviews_match = re.search(r'([\d,]+)\s+Reviews?', reviews_text_combined)
                if ratings_match:
                    total_ratings = int(ratings_match.group(1).replace(',', ''))
                if reviews_match:
                    total_reviews = int(reviews_match.group(1).replace(',', ''))

        # Images
        images = self.extract_product_images(response, ld_json_data)

        # Highlights
        highlights = response.css("ul._1_Y6L > li::text, div._1xgFc9 li::text").getall()
        highlights = [h.strip() for h in highlights if h.strip()]

        # Description - UPDATED SELECTOR
        description_parts = response.css("div.yN\\+eNk.w9jEaj p::text, div._1mXcCf p::text, div._3WHvuP::text").getall()
        description = " ".join([d.strip() for d in description_parts if d.strip()])
        
        if not description:
            # Fallback: try meta description
            meta_desc = response.css("meta[name='Description']::attr(content)").get()
            if meta_desc:
                description = meta_desc.strip()

        # Specifications - UPDATED SELECTORS
        specs = {}
        
        # Try current Flipkart structure (Nov 2025)
        spec_tables = response.css("table._0ZhAN9")
        if spec_tables:
            for table in spec_tables:
                # Get the section title (category like "Display Features", "Camera", etc.)
                section_title_elem = table.xpath("preceding-sibling::*[1]")
                section_title = section_title_elem.css("div._4BJ2V\\+::text").get()
                
                rows = table.css("tr.WJdYP6.row")
                for row in rows:
                    key = row.css("td.\\+fFi1w::text").get()
                    # Values are in nested ul > li structure
                    values = row.css("td.Izz52n ul li.HPETK2::text").getall()
                    value = ", ".join([v.strip() for v in values if v.strip()])
                    
                    if key and value:
                        # Optionally prefix with section title for clarity
                        if section_title:
                            full_key = f"{section_title.strip()} - {key.strip()}"
                        else:
                            full_key = key.strip()
                        specs[full_key] = value
        
        # Fallback to old selectors if nothing found
        if not specs:
            spec_selectors = [
                "table._14cfVK tr",
                "div._2418kt table tr",
                "table.IwbwGp tr",
            ]
            
            for spec_selector in spec_selectors:
                spec_rows = response.css(spec_selector)
                if spec_rows:
                    for row in spec_rows:
                        key = row.css("td:first-child::text, th::text").get()
                        value = row.css("td:last-child::text, td:nth-child(2)::text").get()
                        if key and value:
                            specs[key.strip()] = value.strip()
                    if specs:
                        break

        self.logger.info(f"✅ Extracted {len(specs)} specifications")
        self.logger.info(f"✅ Description length: {len(description)} chars")

        # EXTRACT ALL REVIEWS
        reviews = self.extract_all_reviews(response)

        return {
            "title": title,
            "brand": brand,
            "price": price,
            "price_numeric": price_numeric,
            "availability": availability,
            "rating": float(rating) if rating else None,
            "total_reviews": total_reviews,
            "total_ratings": total_ratings,
            "images": images,
            "highlights": highlights,
            "description": description,
            "specifications": specs,
            "reviews_from_page": reviews
        }

    def extract_product_images(self, response, ld_json_data):
        """Extract product images with priority for higher quality"""
        
        images = []
        
        # JSON-LD first - upgrade to higher quality
        if ld_json_data.get("image"):
            if isinstance(ld_json_data["image"], list):
                images.extend(ld_json_data["image"])
            else:
                images.append(ld_json_data["image"])
            
            # Upgrade image URLs to higher resolution
            upgraded_images = []
            for img in images:
                if img and 'http' in img:
                    # Replace small dimensions with larger ones (832x832 is high quality)
                    img = re.sub(r'/(\d{2,4})/(\d{2,4})/', '/832/832/', img)
                    # Filter out small thumbnails
                    if not any(size in img for size in ['/128/128/', '/200/200/', '/50/', '/100/']):
                        upgraded_images.append(img)
            
            if upgraded_images:
                return upgraded_images[:10]
        
        # Image gallery - upgrade to higher quality
        image_gallery = response.css("div._1AtVbE img::attr(src), div._3li7GG img::attr(src)").getall()
        
        if image_gallery:
            images = [
                img for img in image_gallery 
                if img and ('http' in img or img.startswith('//'))
                and 'rukmini' in img.lower()
                and not any(small in img for small in ['128/128', '50/', '100/', '200/200'])  # Filter out thumbnails
            ]
            
            # Add https protocol if missing
            images = ['https:' + img if img.startswith('//') else img for img in images]
            
            # Upgrade all images to 832x832 (high quality on Flipkart)
            images = [re.sub(r'/(\d{2,4})/(\d{2,4})/', '/832/832/', img) for img in images]
            
            # Remove duplicates while preserving order
            unique_images = list(dict.fromkeys(images))
            
            if unique_images:
                return unique_images[:10]
        
        # Main image - upgrade to higher quality
        main_image = response.css("img._396cs4::attr(src), img._2r_T1I::attr(src)").get()
        if main_image:
            if main_image.startswith('//'):
                main_image = 'https:' + main_image
            # Upgrade to higher resolution
            main_image = re.sub(r'/(\d{2,4})/(\d{2,4})/', '/832/832/', main_image)
            return [main_image]
        
        return []

    def extract_all_reviews(self, response):
        """Extract 10-20+ REAL customer reviews (UPDATED SELECTORS FOR 2025)"""
        
        reviews = []
        
        self.logger.info("🔍 EXTRACTING REVIEWS...")
        
        # UPDATED: Flipkart's current HTML structure (as of Nov 2025)
        review_containers = response.css("div.RcXBOT")
        
        if not review_containers:
            # Fallback
            review_containers = response.css("div.col._2wzgFH")
        
        self.logger.info(f"Found {len(review_containers)} review containers")
        
        for idx, container in enumerate(review_containers, 1):
            # Extract metadata - UPDATED SELECTORS
            title = container.css("p.z9E0IG::text").get()
            rating = container.css("div.XQDdHH.Ga3i8K::text").get()
            
            # Extract review text - Try multiple selectors
            review_text = None
            
            # Method 1: Main review text container
            text_parts = container.css("div.ZmyHeo div::text").getall()
            if text_parts:
                review_text = " ".join([t.strip() for t in text_parts if t.strip()])
            
            # Method 2: Alternative (if layout changed slightly)
            if not review_text or len(review_text) < 15:
                text_parts = container.css("div.t-ZTKy div::text, div._3nrCtb::text").getall()
                if text_parts:
                    review_text = " ".join([t.strip() for t in text_parts if t.strip()])
            
            # Validate review text
            if not review_text or len(review_text) < 15:
                self.logger.debug(f"  ⚠ Container {idx}: No text (len={len(review_text or '')})")
                continue
            
            text_lower = review_text.lower()
            
            # Skip UI elements
            ui_keywords = ['enter pincode', 'buy without', 'please select', 'add to cart', 'currently unavailable']
            if any(kw in text_lower for kw in ui_keywords):
                self.logger.debug(f"  ✗ UI element: {review_text[:30]}...")
                continue
            
            # Skip price-only text
            if review_text.strip().startswith('₹') and len(review_text) < 50:
                continue
            
            # Must have review-like features
            has_review_features = (
                len(review_text) > 30 or
                (title and len(title) > 5) or
                rating or
                any(word in text_lower for word in ['good', 'bad', 'excellent', 'nice', 'product', 'quality', 'recommend', 'phone', 'camera', 'battery'])
            )
            
            if not has_review_features:
                self.logger.debug(f"  ✗ Not review-like: {review_text[:30]}...")
                continue
            
            # Skip if too long
            if len(review_text) > 1200:
                continue
            
            # Extract author and date
            author = container.css("p._2NsDsF.AwS1CA::text").get()
            date_elements = container.css("p._2NsDsF::text").getall()
            date = date_elements[-1] if date_elements else None  # Last one is usually the date
            
            # Check for verified purchase
            verified = bool(container.css("span:contains('Certified Buyer')").get())
            
            # Add review
            reviews.append({
                "title": title.strip() if title else None,
                "rating": rating.strip() if rating else None,
                "text": review_text.strip()[:500],
                "author": author.strip() if author else "Anonymous",
                "date": date.strip() if date else None,
                "verified_purchase": verified
            })
            
            self.logger.info(f"✅ Review {len(reviews)}: {review_text[:60]}...")
            
            # Stop at 25 reviews
            if len(reviews) >= 25:
                break
        
        self.logger.info(f"✅ EXTRACTED {len(reviews)} VALID REVIEWS")
        return reviews

    def extract_json_ld(self, response):
        """Extract JSON-LD"""
        ld_json_text = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if not ld_json_text:
            return {}
        try:
            loaded = json.loads(ld_json_text)
            if isinstance(loaded, list):
                return next((item for item in loaded if item.get('@type') == 'Product'), {})
            return loaded if loaded.get('@type') == 'Product' else {}
        except:
            return {}

    def _extract_price(self, price_string):
        """Extract numeric price"""
        if not price_string:
            return None
        try:
            numeric_str = re.sub(r'[^\d.]', '', str(price_string))
            return float(numeric_str) if numeric_str else None
        except:
            return None

    def errback_handler(self, failure):
        self.logger.error(f"❌ Request failed: {failure}")
