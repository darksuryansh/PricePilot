# Myntra Scraper - Proxy Configuration

## Issue: Myntra Bot Detection on Cloud Servers

Myntra has strong bot detection that blocks requests from datacenter/cloud IPs (like Hugging Face Spaces). 

**Status:**
- ✅ Works locally (residential IPs)
- ❌ Blocked on Hugging Face (datacenter IPs)

## Solution: Add Proxy Support

To enable Myntra scraping on Hugging Face, add a **residential proxy** service:

### Option 1: ScraperAPI (Recommended)
1. Sign up at https://www.scraperapi.com/
2. Get your API key
3. Set environment variable in Hugging Face:
   ```
   PROXY_URL=http://scraperapi:<YOUR_API_KEY>@proxy-server.scraperapi.com:8001
   ```

### Option 2: Bright Data
1. Sign up at https://brightdata.com/
2. Create a residential proxy
3. Set environment variable:
   ```
   PROXY_URL=http://username:password@brd.superproxy.io:22225
   ```

### Option 3: Oxylabs
1. Sign up at https://oxylabs.io/
2. Get proxy credentials
3. Set environment variable:
   ```
   PROXY_URL=http://username:password@pr.oxylabs.io:7777
   ```

## Alternative: Disable Myntra on Cloud

If you don't want to use proxies, update your frontend to show a message:
- "Myntra scraping is temporarily unavailable on cloud deployment"
- Direct users to other platforms: Amazon, Flipkart, Meesho

## Cost Considerations

- **ScraperAPI**: Free tier includes 5,000 requests/month (~$29/mo after)
- **Bright Data**: Pay-as-you-go starting at $500 minimum
- **Oxylabs**: Starting at $99/month

**Recommendation:** Start with ScraperAPI's free tier for testing.
