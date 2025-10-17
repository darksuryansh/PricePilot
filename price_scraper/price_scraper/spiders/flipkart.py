
#scrapy crawl flipkart -a url="https://www.flipkart.com/nothing-phone-3a-white-128-gb/p/itm49557c5a65f9c?pid=MOBH8G3PK4RZFYAA&lid=LSTMOBH8G3PK4RZFYAAWQRDU6&param=9565&ctx=eyJjYXJkQ29udGV4dCI6eyJhdHRyaWJ1dGVzIjp7InZhbHVlQ2FsbG91dCI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ2YWx1ZUNhbGxvdXQiLCJpbmZlcmVuY2VUeXBlIjoiVkFMVUVfQ0FMTE9VVCIsInZhbHVlcyI6WyJGcm9tIOKCuTIyLDk5OSoiXSwidmFsdWVUeXBlIjoiTVVMVElfVkFMVUVEIn19LCJ0aXRsZSI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ0aXRsZSIsImluZmVyZW5jZVR5cGUiOiJUSVRMRSIsInZhbHVlcyI6WyJOb3RoaW5nIFBob25lICgzYSkiXSwidmFsdWVUeXBlIjoiTVVMVElfVkFMVUVEIn19LCJoZXJvUGlkIjp7InNpbmdsZVZhbHVlQXR0cmlidXRlIjp7ImtleSI6Imhlcm9QaWQiLCJpbmZlcmVuY2VUeXBlIjoiUElEIiwidmFsdWUiOiJNT0JIOEczUEs0UlpGWUFBIiwidmFsdWVUeXBlIjoiU0lOR0xFX1ZBTFVFRCJ9fX19fQ==" -o flipkart.json


# import scrapy

# import json
# import re

# API_KEY = "1e2111f03040896d16ef0c94ecfd16ee"

# class FlipkartSpider(scrapy.Spider):
#     name = "flipkart"

#     def __init__(self, url=None, *args, **kwargs):
#         super(FlipkartSpider, self).__init__(*args, **kwargs)
#         self.start_urls = [url]

#     def start_requests(self):
#         for url in self.start_urls:
#             api_url = f"https://api.scraperapi.com/?api_key={API_KEY}&url={url}"
#             yield scrapy.Request(api_url, callback=self.parse, meta={"original_url": url})

#     def parse(self, response):
#         url = response.meta["original_url"]

#         ld_json = response.xpath('//script[@type="application/ld+json"]/text()').get()
#         data = {}
#         if ld_json:
#             try:
#                 loaded = json.loads(ld_json)
#                 # Sometimes it's a list, sometimes a dict
#                 if isinstance(loaded, list):
#                     # Usually first object is product info
#                     data = loaded[0]
#                 else:
#                     data = loaded
#             except Exception as e:
#                 self.logger.error(f"Error parsing JSON: {e}")

#         product_id = re.search(r"/p/itm(\w+)", url)
#         product_id = product_id.group(1) if product_id else None

#         yield {
#             "product_id": product_id,
#             "title": data.get("name"),
#             "brand": data.get("brand", {}).get("name") if isinstance(data.get("brand"), dict) else data.get("brand"),
#             "price": data.get("offers", {}).get("price") if isinstance(data.get("offers"), dict) else None,
#             "availability": data.get("offers", {}).get("availability") if isinstance(data.get("offers"), dict) else None,
#             "total_reviews": data.get("aggregateRating", {}).get("reviewCount") if isinstance(data.get("aggregateRating"), dict) else None,
#             "images": data.get("image"),
#             "url": url,
# 
# 
#         }

import scrapy
import json
import re

# IMPORTANT: Keep your API key secure and do not share it publicly.
API_KEY = "1e2111f03040896d16ef0c94ecfd16ee"

class FlipkartSpider(scrapy.Spider):
    name = "flipkart"

    def __init__(self, url=None, *args, **kwargs):
        super(FlipkartSpider, self).__init__(*args, **kwargs)
        # Ensure a URL is provided when running the spider
        if url:
            self.start_urls = [url]
        else:
            self.logger.error("No URL provided. Please run with: -a url='<your_url>'")
            self.start_urls = []

    def start_requests(self):
        # This loop will not run if self.start_urls is empty
        for url in self.start_urls:
            api_url = f"http://api.scraperapi.com/?api_key={API_KEY}&url={url}"
            yield scrapy.Request(api_url, callback=self.parse, meta={"original_url": url})

    def parse(self, response):
        original_url = response.meta["original_url"]

        # --- 1. Primary Data Source: Embedded JSON (ld+json) ---
        ld_json_text = response.xpath('//script[@type="application/ld+json"]/text()').get()
        data = {}
        if ld_json_text:
            try:
                loaded = json.loads(ld_json_text)
                # Find the main 'Product' dictionary if the JSON contains a list
                if isinstance(loaded, list):
                    data = next((item for item in loaded if item.get('@type') == 'Product'), {})
                else:
                    data = loaded
            except json.JSONDecodeError:
                self.logger.warning("Could not parse ld+json data.")

        # --- 2. Data Extraction with CSS Fallbacks ---
        
        # Helper function for safe dictionary access
        def get_nested(d, *keys):
            for key in keys:
                if isinstance(d, dict):
                    d = d.get(key)
                else:
                    return None
            return d

        # Product ID (from URL)
        product_id = re.search(r"pid=([A-Z0-9]+)", original_url).group(1) if re.search(r"pid=([A-Z0-9]+)", original_url) else None

        # Title
        title = get_nested(data, "name") or response.css("span.B_NuCI::text").get()

        # Brand
        brand = get_nested(data, "brand", "name") or (title.split()[0] if title else None)

        # Price
        price_str = get_nested(data, "offers", "price") or response.css("div._30jeq3._16Jk6d::text").get()
        price = None
        if price_str:
            # Clean the price string (e.g., "₹22,999" -> 22999)
            price = float(re.sub(r'[^\d.]', '', str(price_str)))

        # Rating & Reviews
        rating = get_nested(data, "aggregateRating", "ratingValue") or response.css("div._3LWZlK::text").get()
        total_reviews = get_nested(data, "aggregateRating", "reviewCount")
        if not total_reviews:
            # Extract review/rating counts from text like "9,880 Ratings & 958 Reviews"
            reviews_text = response.css('span._2_R_DZ::text').get()
            if reviews_text:
                match = re.search(r'([\d,]+)\s+Reviews', reviews_text)
                if match:
                    total_reviews = int(match.group(1).replace(',', ''))
        
        # Availability
        availability = get_nested(data, "offers", "availability")
        if not availability:
            # Check for "Sold Out" or "Out of Stock" text on the page
            if response.css('div._16FRp0').get():
                availability = "http://schema.org/OutOfStock"
            else:
                availability = "http://schema.org/InStock"

        # Images
        images = get_nested(data, "image") or response.css("img._396cs4._2amPTt._3qGmMb::attr(src)").getall()


        # --- 3. Yield Final Scraped Item ---
        yield {
            "product_id": product_id.strip() if product_id else None,
            "title": title.strip() if title else None,
            "brand": brand.strip() if brand else None,
            "price": price,
            "rating": float(rating) if rating else None,
            "total_reviews": int(total_reviews) if total_reviews else None,
            "availability": availability,
            "images": images,
            "url": original_url,
        }