# import scrapy
# from scrapy_playwright.page import PageMethod

# class MyntraSpider(scrapy.Spider):
#     name = 'myntra'

#     async def start(self):
#         url = 'https://www.myntra.com/proteins/muscleblaze/muscleblaze-biozyme-performance-rich-chocolate-whey-protein-powder-1kg/25248982/buy'
#         yield scrapy.Request(
#             url,
#             callback=self.parse,
#             meta=dict(
#                 playwright=True,
#                 playwright_include_page=True,
#                 playwright_page_methods=[
#                     PageMethod('wait_for_selector', 'h1.pdp-title'),
#                 ],
#             )
#         )

#     async def parse(self, response):
#         yield {
#             'website': 'Myntra',
#             'title': response.css('h1.pdp-title::text').get('').strip(),
#             'price': response.css('span.pdp-price strong::text').get('').strip(),   
#             'image_url': response.css('div.image-grid-image img::attr(src)').get('')
#         }




#scrapy crawl myntra -a url="https://www.myntra.com/watches/wrogn/wrogn-men-blue-printed-dial--steel-toned-stainless-steel-straps-analogue-watch-wrg00107a/16109462/buy" -o myntra.json

import scrapy
import json
import re

# IMPORTANT: Keep your API key secure and do not share it publicly.
API_KEY = "1e2111f03040896d16ef0c94ecfd16ee"

class MyntraSpider(scrapy.Spider):
    name = "myntra"

    def __init__(self, url=None, *args, **kwargs):
        super(MyntraSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            self.logger.error("No URL provided. Please run with: -a url='<your_url>'")
            self.start_urls = []

    def start_requests(self):
        for url in self.start_urls:
            # THE FIX: Added '&premium=true' to use higher-quality proxies
            api_url = f"http://api.scraperapi.com/?api_key={API_KEY}&url={url}&render=true&premium=true"
            yield scrapy.Request(api_url, callback=self.parse, meta={"original_url": url})

    def parse(self, response):
        # ... (The rest of the parse method remains exactly the same) ...
        original_url = response.meta["original_url"]

        ld_json_text = response.xpath('//script[@type="application/ld+json"]/text()').get()
        data = {}
        if ld_json_text:
            try:
                data = json.loads(ld_json_text)
            except json.JSONDecodeError:
                self.logger.warning("Could not parse ld+json data on Myntra page.")

        def get_nested(d, *keys):
            for key in keys:
                if isinstance(d, dict):
                    d = d.get(key)
                else:
                    return None
            return d
            
        product_id_match = re.search(r'/(\d+)/buy', original_url)
        product_id = product_id_match.group(1) if product_id_match else None

        brand = get_nested(data, "brand", "name") or response.css('h1.pdp-title::text').get()
        title = get_nested(data, "name") or response.css('h1.pdp-name::text').get()

        price_str = get_nested(data, "offers", "price") or response.css('span.pdp-price strong::text').get()
        price = None
        if price_str:
            price = float(re.sub(r'[^\d.]', '', str(price_str)))

        rating = get_nested(data, "aggregateRating", "ratingValue") or response.css('div.index-averageRating::text').get()
        
        review_count_str = get_nested(data, "aggregateRating", "ratingCount") or response.css('div.index-ratingsCount::text').get()
        review_count = 0
        if review_count_str:
            count_text = str(review_count_str).lower().replace('ratings', '').strip()
            if 'k' in count_text:
                num = float(count_text.replace('k', ''))
                review_count = int(num * 1000)
            else:
                review_count = int(re.sub(r'\D', '', count_text))

        images = get_nested(data, "image")

        yield {
            "product_id": product_id,
            "brand": brand.strip() if brand else None,
            "title": title.strip() if title else None,
            "price": price,
            "rating": float(rating) if rating else None,
            "review_count": review_count,
            "images": images,
            "url": original_url,
        }