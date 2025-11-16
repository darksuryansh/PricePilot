# Universal Product Scraper - Scrapes one product and finds it on other platforms
# Usage: scrapy crawl universal -a url="<any_product_url>"

import re
import scrapy
import json
from urllib.parse import urlparse, quote_plus

class UniversalSpider(scrapy.Spider):
    name = "universal"
    
    # Platform search URLs
    SEARCH_URLS = {
        'amazon': 'https://www.amazon.in/s?k={}',
        'flipkart': 'https://www.flipkart.com/search?q={}',
        'meesho': 'https://www.meesho.com/search?q={}',
        'myntra': 'https://www.myntra.com/{}',
    }
    
    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not url:
            raise ValueError("URL is required. Usage: scrapy crawl universal -a url='<product_url>'")
        
        self.original_url = url
        self.source_platform = self.identify_platform(url)
        
        self.logger.info(f"🔍 Universal Scraper Started")
        self.logger.info(f"📍 Source Platform: {self.source_platform}")
        self.logger.info(f"🔗 Original URL: {url}")
        
        # Store results from all platforms
        self.main_product = None
        self.search_query = None
        self.comparison_results = []
    
    def identify_platform(self, url):
        """Identify which platform the URL belongs to"""
        domain = urlparse(url).netloc.lower()
        
        if 'amazon' in domain:
            return 'amazon'
        elif 'flipkart' in domain:
            return 'flipkart'
        elif 'meesho' in domain:
            return 'meesho'
        elif 'myntra' in domain:
            return 'myntra'
        else:
            return 'unknown'
    
    def start_requests(self):
        """Start by scraping the original product"""
        self.logger.info(f"🚀 Step 1: Scraping original product from {self.source_platform}")
        
        # Scrape the original product based on platform
        yield scrapy.Request(
            self.original_url,
            callback=self.parse_original_product,
            meta={
                'platform': self.source_platform,
                'playwright': True if self.source_platform in ['flipkart', 'meesho', 'myntra'] else False,
                'playwright_page_goto_kwargs': {
                    'wait_until': 'networkidle',
                    'timeout': 60000,
                } if self.source_platform in ['flipkart', 'meesho', 'myntra'] else None,
            },
            dont_filter=True,
            errback=self.errback_handler
        )
    
    def parse_original_product(self, response):
        """Parse the original product and extract search query"""
        platform = response.meta['platform']
        
        self.logger.info(f"✅ Successfully loaded {platform} product page")
        
        # Extract title and brand for search query
        if platform == 'amazon':
            title = response.css('#productTitle::text').get()
            brand = response.css('a#bylineInfo::text, tr.po-brand td.a-span9 span::text').get()
            
        elif platform == 'flipkart':
            title = response.css('span.VU-ZEz::text, h1.yhB1nd::text, span.B_NuCI::text').get()
            brand = response.css('div._2B099V a::text, span.G6XhRU span::text').get()
            
        elif platform == 'meesho':
            title = response.css('h1.sc-eDvSVe::text, span.sc-eDvSVe::text').get()
            brand = response.css('div[class*="ProductDetail"] p::text').get()
            
        elif platform == 'myntra':
            title = response.css('h1.pdp-title::text, h1.pdp-name::text').get()
            brand = response.css('h1.pdp-title::text, h1.pdp-name::text').get()
        
        # Clean and prepare search query
        if title:
            title = title.strip()
            brand = brand.strip() if brand else ""
            
            # Create search query (brand + key words from title)
            search_query = f"{brand} {title}".strip()
            
            # Clean search query - remove special chars and extra words
            search_query = re.sub(r'\([^)]*\)', '', search_query)  # Remove parentheses content
            search_query = re.sub(r'[^\w\s]', ' ', search_query)   # Remove special chars
            search_query = ' '.join(search_query.split()[:8])       # Keep first 8 words
            
            self.search_query = search_query
            self.logger.info(f"🔎 Search Query: {search_query}")
            
            # Store main product info
            self.main_product = {
                'platform': platform,
                'url': self.original_url,
                'title': title,
                'brand': brand,
                'search_query': search_query
            }
            
            # Now search for this product on other platforms
            yield from self.search_other_platforms()
        else:
            self.logger.error(f"❌ Could not extract product title from {platform}")
    
    def search_other_platforms(self):
        """Search for the product on other e-commerce platforms"""
        self.logger.info(f"🚀 Step 2: Searching for product on other platforms")
        
        other_platforms = [p for p in ['amazon', 'flipkart', 'meesho', 'myntra'] 
                          if p != self.source_platform]
        
        for platform in other_platforms:
            search_url = self.SEARCH_URLS[platform].format(quote_plus(self.search_query))
            
            self.logger.info(f"🔍 Searching {platform}: {search_url}")
            
            yield scrapy.Request(
                search_url,
                callback=self.parse_search_results,
                meta={
                    'platform': platform,
                    'playwright': True if platform in ['flipkart', 'meesho', 'myntra'] else False,
                    'playwright_page_goto_kwargs': {
                        'wait_until': 'networkidle',
                        'timeout': 60000,
                    } if platform in ['flipkart', 'meesho', 'myntra'] else None,
                },
                dont_filter=True,
                errback=self.errback_handler
            )
    
    def parse_search_results(self, response):
        """Parse search results and extract the best matching product"""
        platform = response.meta['platform']
        
        self.logger.info(f"📋 Parsing {platform} search results")
        
        # Extract first product link based on platform
        product_url = None
        
        if platform == 'amazon':
            # Amazon search result selector
            product_url = response.css('div[data-component-type="s-search-result"] h2 a::attr(href)').get()
            if product_url:
                product_url = f"https://www.amazon.in{product_url}"
                
        elif platform == 'flipkart':
            # Flipkart search result selector
            product_url = response.css('a._1fQZEK::attr(href), a.s1Q9rs::attr(href), a._2rpwqI::attr(href)').get()
            if product_url and not product_url.startswith('http'):
                product_url = f"https://www.flipkart.com{product_url}"
                
        elif platform == 'meesho':
            # Meesho search result selector
            product_url = response.css('a[href*="/product/"]::attr(href)').get()
            if product_url and not product_url.startswith('http'):
                product_url = f"https://www.meesho.com{product_url}"
                
        elif platform == 'myntra':
            # Myntra search result selector
            product_url = response.css('a.product-base::attr(href), li.product-base a::attr(href)').get()
            if product_url and not product_url.startswith('http'):
                product_url = f"https://www.myntra.com/{product_url}"
        
        if product_url:
            self.logger.info(f"✅ Found product on {platform}: {product_url}")
            
            # Now scrape this product
            yield scrapy.Request(
                product_url,
                callback=self.parse_comparison_product,
                meta={
                    'platform': platform,
                    'playwright': True if platform in ['flipkart', 'meesho', 'myntra'] else False,
                    'playwright_page_goto_kwargs': {
                        'wait_until': 'networkidle',
                        'timeout': 60000,
                    } if platform in ['flipkart', 'meesho', 'myntra'] else None,
                },
                dont_filter=True,
                errback=self.errback_handler
            )
        else:
            self.logger.warning(f"⚠ No products found on {platform}")
    
    def parse_comparison_product(self, response):
        """Parse the comparison product and extract price info"""
        platform = response.meta['platform']
        
        self.logger.info(f"💰 Extracting price from {platform}")
        
        # Extract basic info based on platform
        if platform == 'amazon':
            title = response.css('#productTitle::text').get()
            price = response.css('span.a-price-whole::text').get()
            rating = response.css('span.a-icon-alt::text').get()
            
        elif platform == 'flipkart':
            title = response.css('span.VU-ZEz::text, h1.yhB1nd::text').get()
            price = response.css('div.Nx9bqj::text').get()
            rating = response.css('div.XQDdHH::text').get()
            
        elif platform == 'meesho':
            title = response.css('h1.sc-eDvSVe::text').get()
            price = response.css('span[class*="ProductPrice"]::text, span.sc-jrsJWt::text').get()
            rating = response.css('span[class*="Rating"]::text, p.sc-fmzyuX::text').get()
            
        elif platform == 'myntra':
            title = response.css('h1.pdp-title::text, h1.pdp-name::text').get()
            price = response.css('span.pdp-price strong::text').get()
            rating = response.css('div.index-overallRating div::text').get()
        
        # Store comparison result
        if title and price:
            title = title.strip()
            price_clean = re.sub(r'[^\d.]', '', price)
            price_numeric = float(price_clean) if price_clean else None
            
            comparison_data = {
                'platform': platform,
                'url': response.url,
                'title': title,
                'price': price.strip(),
                'price_numeric': price_numeric,
                'rating': rating.strip() if rating else None
            }
            
            self.comparison_results.append(comparison_data)
            self.logger.info(f"✅ {platform}: {title} - ₹{price_numeric}")
        
    def closed(self, reason):
        """Called when spider closes - output final comparison"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🎯 PRICE COMPARISON RESULTS")
        self.logger.info(f"{'='*60}")
        
        if self.main_product:
            self.logger.info(f"\n📍 Original Product:")
            self.logger.info(f"   Platform: {self.main_product['platform']}")
            self.logger.info(f"   Query: {self.main_product['search_query']}")
        
        self.logger.info(f"\n💰 Price Comparison:")
        self.logger.info(f"   Found on {len(self.comparison_results)} other platform(s)")
        
        for result in sorted(self.comparison_results, key=lambda x: x['price_numeric'] or float('inf')):
            self.logger.info(f"\n   {result['platform'].upper()}:")
            self.logger.info(f"   Price: ₹{result['price_numeric']}")
            self.logger.info(f"   Rating: {result['rating']}")
            self.logger.info(f"   URL: {result['url']}")
        
        # Calculate savings
        if len(self.comparison_results) > 1:
            prices = [r['price_numeric'] for r in self.comparison_results if r['price_numeric']]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                savings = max_price - min_price
                savings_pct = (savings / max_price) * 100
                
                self.logger.info(f"\n💡 Potential Savings:")
                self.logger.info(f"   Min Price: ₹{min_price}")
                self.logger.info(f"   Max Price: ₹{max_price}")
                self.logger.info(f"   You can save: ₹{savings} ({savings_pct:.1f}%)")
        
        self.logger.info(f"\n{'='*60}")
    
    def errback_handler(self, failure):
        self.logger.error(f"❌ Request failed: {failure}")

