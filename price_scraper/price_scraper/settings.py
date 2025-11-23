# Scrapy settings for price_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "price_scraper"

SPIDER_MODULES = ["price_scraper.spiders"]
NEWSPIDER_MODULE = "price_scraper.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "price_scraper.middlewares.PriceScraperSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "price_scraper.middlewares.PriceScraperDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'price_scraper.pipelines.MongoPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
# DOWNLOAD_HANDLERS = {
#     "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
# }


# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#   'Accept-Language': 'en-US,en;q=0.9',
#   'Accept-Encoding': 'gzip, deflate, br',
#   'Upgrade-Insecure-Requests': '1',
#   'Sec-Fetch-Site': 'same-origin',
#   'Sec-Fetch-Mode': 'navigate',
#   'Sec-Fetch-User': '?1',
#   'Sec-Fetch-Dest': 'document',
# }

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
ROTATING_PROXY_LIST = [
    "http://user:pass@proxy1:port",
    "http://user:pass@proxy2:port",
]
SCRAPER_API_KEY = "1e2111f03040896d16ef0c94ecfd16ee"   # <-- replace with your real key
HTTPERROR_ALLOWED_CODES = [400, 403, 404]
# settings.py



# ... (your other settings like BOT_NAME) ...

# You already have these, they are correct
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True
}
PLAYWRIGHT_CONTEXTS = {
    "persistent": {
        "user_data_dir": "playwright_user_data"
    }
}

# === ⬇️ ADD THIS ONE LINE ⬇️ ===
# This tells Playwright to use Firefox instead of Chromium
PLAYWRIGHT_BROWSER_TYPE = "firefox"
# === ⬆️ END OF NEW LINE ⬆️ ===


# ... (your other settings like PIPELINES) ...

# Scrapy settings for amazon project
# Scrapy settings for price_scraper project

BOT_NAME = 'price_scraper'

SPIDER_MODULES = ['price_scraper.spiders']
NEWSPIDER_MODULE = 'price_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure delays and concurrency
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# User agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

# Playwright configuration
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Use Chromium instead of Firefox (better for bot detection avoidance)
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 60000,
    # Chromium args to avoid detection
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-gpu",
    ]
}

# Remove persistent context to avoid profile conflicts
# Each run will use a fresh browser instance
PLAYWRIGHT_CONTEXTS = {
    "default": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "geolocation": {"longitude": -73.935242, "latitude": 40.730610},
        "permissions": ["geolocation"],
        "ignore_https_errors": True,
        "java_script_enabled": True,
    }
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Configure pipelines (optional - comment out if you don't need it)
# ITEM_PIPELINES = {
#     'price_scraper.pipelines.PriceScraperPipeline': 300,
# }

# Retry configuration
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]

# Logging
LOG_LEVEL = 'INFO'

# Disable cookies (can help avoid detection)
COOKIES_ENABLED = False

# Set maximum concurrent requests
CONCURRENT_REQUESTS_PER_IP = 1

# Configure pipelines
ITEM_PIPELINES = {
    'price_scraper.pipelines.MongoPipeline': 300,
    'price_scraper.pipelines.JsonExportPipeline': 400,  # Optional: also export to JSON
}
