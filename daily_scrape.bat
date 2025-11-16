@echo off
cd C:\pc\Price_tracker\price_scraper
call conda activate webdev

echo ========================================
echo Starting Daily Price Tracking
echo Time: %date% %time%
echo ========================================

REM Create logs directory if not exists
if not exist "logs" mkdir logs

REM Scrape Amazon products
echo [1/3] Scraping Amazon...
scrapy crawl amazon -a url="YOUR_AMAZON_URL_1" -a api_key="24356f5fddmsh6afec693b34efc7p1a8ebejsn06df89b3fe15" >> logs/amazon_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1

REM Scrape Flipkart products
echo [2/3] Scraping Flipkart...
scrapy crawl flipkart -a url="YOUR_FLIPKART_URL_1" -a api_key="24356f5fddmsh6afec693b34efc7p1a8ebejsn06df89b3fe15" >> logs/flipkart_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1

REM Scrape Myntra products
echo [3/3] Scraping Myntra...
scrapy crawl myntra -a url="YOUR_MYNTRA_URL_1" -a api_key="24356f5fddmsh6afec693b34efc7p1a8ebejsn06df89b3fe15" >> logs/myntra_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1

echo ========================================
echo Daily scraping completed!
echo ========================================
pause
