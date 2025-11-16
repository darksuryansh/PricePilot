# # import scrapy
# # import json
# # import re

# # # IMPORTANT: Keep your API key secure and do not share it publicly.
# # API_KEY = "1e2111f03040896d16ef0c94ecfd16ee"

# # class MeeshoSpider(scrapy.Spider):
# #     name = "meesho"

# #     def __init__(self, url=None, *args, **kwargs):
# #         super(MeeshoSpider, self).__init__(*args, **kwargs)
# #         if url:
# #             self.start_urls = [url]
# #         else:
# #             self.logger.error("No URL provided. Please run with: -a url='<your_url>'")
# #             self.start_urls = []

# #     def start_requests(self):
# #         for url in self.start_urls:
# #             # THE FIX: Added '&country_code=in' to make the request from India
# #             api_url = f"http://api.scraperapi.com/?api_key={API_KEY}&url={url}&render=true&premium=true&country_code=in"
# #             yield scrapy.Request(api_url, callback=self.parse, meta={"original_url": url})

# #     def parse(self, response):
# #         # ... (The rest of the parse method remains exactly the same) ...
# #         original_url = response.meta["original_url"]

# #         ld_json_text = response.xpath('//script[@type="application/ld+json"]/text()').get()
# #         data = {}
# #         if ld_json_text:
# #             try:
# #                 data = json.loads(ld_json_text)
# #             except json.JSONDecodeError:
# #                 self.logger.warning("Could not parse ld+json data on Meesho page.")

# #         def get_nested(d, *keys):
# #             for key in keys:
# #                 if isinstance(d, dict):
# #                     d = d.get(key)
# #                 else:
# #                     return None
# #             return d

# #         product_id_match = re.search(r'/p/(\w+)', original_url)
# #         product_id = product_id_match.group(1) if product_id_match else None

# #         title = get_nested(data, "name") or response.css('span[class*="ProductTitle"]::text').get()

# #         price_str = get_nested(data, "offers", "lowPrice") or response.css('h4[class*="Price"]::text').get()
# #         price = None
# #         if price_str:
# #             price = float(re.sub(r'[^\d.]', '', str(price_str)))
        
# #         rating = get_nested(data, "aggregateRating", "ratingValue")
# #         if not rating:
# #             rating_text = response.css('span[class*="Rating__StyledRating-"]::text').get()
# #             if rating_text:
# #                 rating_match = re.search(r'(\d\.?\d*)', rating_text)
# #                 if rating_match:
# #                     rating = float(rating_match.group(1))

# #         review_count = get_nested(data, "aggregateRating", "ratingCount")
# #         if not review_count:
# #             review_text = response.css('span[class*="TotalRatings__StyledTotalRatings-"]::text').get()
# #             if review_text:
# #                 review_count = int(re.sub(r'\D', '', review_text))

# #         images = get_nested(data, "image")

# #         yield {
# #             "product_id": product_id,
# #             "title": title.strip() if title else None,
# #             "price": price,
# #             "rating": float(rating) if rating else None,
# #             "review_count": int(review_count) if review_count else None,
# #             "images": images,
# #             "url": original_url,
# #         }

# import scrapy
# import json
# import re

# # This is the final, corrected spider for Meesho using modern scrapy-playwright features.
# class MeeshoSpider(scrapy.Spider):
#     name = "meesho"

#     # --- Browser Interaction Functions ---

#     async def hide_automation_flags(self, page, request):
#         """
#         This function runs inside the browser and uses JavaScript to hide
#         common signs that the browser is being automated.
#         """
#         await page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

#     async def add_human_like_wait(self, page, request):
#         """
#         This function adds a simple pause to mimic human browsing behavior,
#         which can help bypass certain anti-bot timing checks.
#         """
#         await page.wait_for_timeout(5000)  # Wait for 5 seconds

#     # --- Scrapy Request and Parsing Logic ---

#     def start_requests(self):
#         url = getattr(self, "url", None)
#         if url:
#             # We pass our new functions in a list to the 'playwright_page_coroutines' meta key.
#             # They will be executed in order.
#             yield scrapy.Request(
#                 url,
#                 meta={
#                     "playwright": True,
#                     "playwright_page_coroutines": [
#                         self.hide_automation_flags,
#                         self.add_human_like_wait,
#                     ]
#                 }
#             )
#         else:
#             self.logger.error("No URL provided. Please run with: -a url='<your_url>'")

#     def parse(self, response):
#         # The parse method remains the same.
#         ld_json_text = response.xpath('//script[@type="application/ld+json"]/text()').get()
#         data = {}
#         if ld_json_text:
#             try:
#                 data = json.loads(ld_json_text)
#             except json.JSONDecodeError:
#                 self.logger.warning("Could not parse ld+json data on Meesho page.")

#         def get_nested(d, *keys):
#             for key in keys:
#                 if isinstance(d, dict):
#                     d = d.get(key)
#                 else:
#                     return None
#             return d

#         product_id_match = re.search(r'/p/(\w+)', response.url)
#         product_id = product_id_match.group(1) if product_id_match else None
#         title = get_nested(data, "name") or response.css('span[class*="ProductTitle"]::text').get()
#         price_str = get_nested(data, "offers", "lowPrice") or response.css('h4[class*="Price"]::text').get()
#         price = None
#         if price_str:
#             price = float(re.sub(r'[^\d.]', '', str(price_str)))
#         rating = get_nested(data, "aggregateRating", "ratingValue")
#         review_count = get_nested(data, "aggregateRating", "ratingCount")

#         yield {
#             "product_id": product_id,
#             "title": title.strip() if title else None,
#             "price": price,
#             "rating": float(rating) if rating else None,
#             "review_count": int(review_count) if review_count else None,
#             "url": response.url,
#         }