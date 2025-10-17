

# #scrapy crawl amazon -a url="https://www.amazon.in/Kitchen-Manufacturer-Warranty-capacity-SF400/dp/B083C6XMKQ/ref=zg_bs_c_kitchen_d_sccl_1/257-8163141-6914053?pd_rd_w=rvdE8&content-id=amzn1.sym.7f3d66f6-5df6-41bc-b3bc-9782a34ce834&pf_rd_p=7f3d66f6-5df6-41bc-b3bc-9782a34ce834&pf_rd_r=5JJ8J1ADJEY5NNXP5XMZ&pd_rd_wg=RG1TA&pd_rd_r=a572ace5-759e-4759-9b4b-6b78937b44bc&pd_rd_i=B083C6XMKQ&th=1" -o amazon.json


    
import re
import json
import scrapy


class AmazonSpider(scrapy.Spider):
    name = "amazon"

    def __init__(self, url=None, api_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = "1e2111f03040896d16ef0c94ecfd16ee"
        self.url = url
        # Add render=true to the initial request as well
        self.start_urls = [
            f"https://api.scraperapi.com/?api_key={self.api_key}&render=true&url={url}"
        ]

    def parse(self, response):
        asin_match = re.search(r"/dp/([A-Z0-9]{10})", response.url)
        asin = asin_match.group(1) if asin_match else None

        title = response.css("#productTitle::text").get()
        if title:
            title = title.strip()

        brand = response.css("#bylineInfo::text").get()
        price = response.css(".a-price .a-offscreen::text").get()
        availability = response.css("#availability span::text").get()
        if availability:
            availability = availability.strip()

        total_reviews = response.css("#acrCustomerReviewText::text").get()
        if total_reviews:
            total_reviews = total_reviews.strip()

        images = []
        img_data = response.css("#imgTagWrapperId img::attr(data-a-dynamic-image)").get()
        if img_data:
            try:
                img_json = json.loads(img_data)
                images = list(img_json.keys())
            except Exception:
                pass

        # Store product details
        product_info = {
            "asin": asin,
            "title": title,
            "brand": brand,
            "price": price,
            "availability": availability,
            "total_reviews": total_reviews,
            "images": images,
            "url": response.url,
            "reviews": [],
        }

        if asin:
            # Build review URL with render=true
            reviews_url = (
                f"https://api.scraperapi.com/?api_key={self.api_key}&render=true&url=https://www.amazon.in/product-reviews/{asin}/?pageNumber=1"
            )
            yield scrapy.Request(
                reviews_url,
                callback=self.parse_reviews,
                meta={"product_info": product_info, "page": 1, "asin": asin},
            )
        else:
            yield product_info

    def parse_reviews(self, response):
        product_info = response.meta["product_info"]
        page = response.meta["page"]
        asin = response.meta["asin"]

        # Try multiple selector patterns for reviews
        # Pattern 1: Standard review format
        reviews = response.css('[data-hook="review"]')
        
        if not reviews:
            # Pattern 2: Alternative review container
            reviews = response.css('.review')
        
        self.logger.info(f"Found {len(reviews)} reviews on page {page}")
        
        for review in reviews:
            # Try multiple selector patterns for each field
            title = (review.css('[data-hook="review-title"] span::text').get() or
                    review.css('.review-title span::text').get() or
                    review.css('.review-title::text').get())
            
            rating = (review.css('[data-hook="review-star-rating"] span::text').get() or
                     review.css('.review-rating span::text').get() or
                     review.css('i[data-hook="review-star-rating"] span::text').get())
            
            # Get review text - try multiple patterns
            text_parts = (review.css('[data-hook="review-body"] span::text').getall() or
                         review.css('.review-text-content span::text').getall() or
                         review.css('.review-text span::text').getall())
            
            text = " ".join(text_parts).strip() if text_parts else None
            
            if text:  # Only add if we have review text
                product_info["reviews"].append(
                    {
                        "title": title.strip() if title else None,
                        "rating": rating.strip() if rating else None,
                        "text": text,
                    }
                )
                self.logger.info(f"Scraped review: {title[:50] if title else 'No title'}...")

        # Check for next page
        next_page = response.css('li.a-last a::attr(href)').get()
        if next_page and page < 5:  # Limit to 5 pages to avoid too many requests
            next_page_url = f"https://api.scraperapi.com/?api_key={self.api_key}&render=true&url=https://www.amazon.in{next_page}"
            yield scrapy.Request(
                next_page_url,
                callback=self.parse_reviews,
                meta={"product_info": product_info, "page": page + 1, "asin": asin},
            )
        else:
            yield product_info


