# 🚀 Quick Start Guide - AI-Powered Product Insights

## Prerequisites
- Gemini API key (free tier available)
- Flask backend running
- React frontend running
- MongoDB running

## 1. Get Your Gemini API Key (2 minutes)

### Option A: Using Browser
1. Open https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Get API Key" or "Create API Key"
4. Copy the key (starts with `AIza...`)

### Option B: Quick Link
Visit: https://aistudio.google.com/app/apikey

## 2. Configure API Key (1 minute)

Open `.env` file and update:

```env
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Replace `your_gemini_api_key_here` with your actual key.

## 3. Restart Backend (30 seconds)

### Terminal 1 - Stop Flask (if running)
```powershell
# Press Ctrl+C in the Flask terminal
```

### Terminal 1 - Start Flask
```powershell
cd c:\pc\Price_tracker
conda activate webdev
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
🤖 Gemini API configured successfully
```

## 4. Test AI Insights (2 minutes)

### Step 1: Scrape a Product
1. Open frontend: http://localhost:5173
2. Paste Amazon product URL (use one with many reviews)
3. Click "Track Product"
4. Wait for scraping to complete

### Step 2: View AI Insights
1. Product comparison page will open automatically
2. Look for "AI Product Insights" card
3. Click on "Summary" tab (if not already selected)
4. You should see:
   - ✅ AI-generated summary
   - ✅ "Should I Buy This?" card with YES/NO/MAYBE
   - ✅ AI Recommendation Score (1-10)
   - ✅ "AI Generated" badge
   - ✅ Target buyer profile
   - ✅ Key considerations

### Step 3: Explore Other Tabs
- **Pros** - What customers love
- **Cons** - Points to consider
- **Features** - Key specifications
- **Ratings** - Rating breakdown

## 5. Example Products to Test

### Good for Testing (High Reviews)
```
Amazon Kitchen Scale:
https://www.amazon.in/Kitchen-Manufacturer-Warranty-capacity-SF400/dp/B083C6XMKQ

OnePlus Earbuds:
https://www.amazon.in/OnePlus-Wireless-Earbuds-Drivers-Playback/dp/B0C8JB3G5W
```

## Expected Results

### With AI Enabled ✅
```
Summary: "This kitchen scale receives overwhelmingly positive reviews..."

Should I Buy This? YES ✅

Reasoning: "Highly recommended for home use based on consistent 
positive feedback about accuracy and functionality..."

AI Recommendation Score: 8/10 🟢
[AI Generated Badge]

Best for: Budget-conscious buyers and home bakers

Key Considerations:
• Designed for personal use only
• Battery-powered, batteries included  
• May not be ideal for items over 3kg
```

### Without AI (Fallback) ⚠️
```
Summary: "This product has 50 customer reviews with an average 
rating of 4.1/5..."

Should I Buy This? MAYBE ⚠️

Reasoning: "Good choice with satisfied customers."

AI Recommendation Score: 7/10 🟡
```

## Troubleshooting

### Issue: "AI insights not available yet"
**Solution:** 
- Check `.env` file has correct API key
- Restart Flask backend
- Check Flask terminal for errors

### Issue: AI insights show basic analysis
**Cause:** Gemini API key not configured or invalid

**Check:**
```powershell
# In Flask terminal, look for:
⚠️ Gemini API key not configured. Using basic analysis.
```

**Fix:**
1. Verify API key in `.env`
2. Check key is valid on Google AI Studio
3. Restart Flask

### Issue: Takes too long (>30 seconds)
**Normal:** AI analysis can take 5-15 seconds
**Too long:** Check internet connection

### Issue: JSON parsing errors
**Check Flask terminal for:**
```
❌ Error generating AI insights: ...
```

**Usually auto-recovers:** Falls back to basic analysis

## Verifying AI is Working

### Method 1: Check Flask Terminal
Look for these messages:
```
🤖 Generating AI insights for {product_name}...
✓ AI insights generated successfully
```

### Method 2: Check Frontend
Look for these indicators:
1. ✨ "AI Generated" badge appears
2. "Should I Buy This?" card shows YES/NO clearly
3. Target buyer field is specific (not "General consumers")
4. Pros/Cons are detailed and specific

### Method 3: Check Browser Console (F12)
```javascript
// Should see:
{
  ai_generated: true,
  buy_recommendation: "YES",
  target_buyer: "Budget-conscious buyers",
  // ... more fields
}
```

## What to Expect

### Analysis Time
- **Without cache:** 5-15 seconds first time
- **Scraping:** 30-60 seconds
- **Total first view:** ~45-75 seconds

### Quality Factors
- **More reviews = Better analysis**
- Minimum 5 reviews recommended
- Ideal: 15+ reviews
- Best: 50+ reviews

### AI Capabilities
- ✅ Sentiment analysis
- ✅ Pattern recognition
- ✅ Specific pros/cons extraction
- ✅ Value assessment
- ✅ Target audience identification
- ✅ Risk identification

## API Key Info

### Free Tier Limits
- **60 requests/minute**
- **1 million tokens/month**
- **~500 products/month free**

### Monitoring Usage
Visit: https://aistudio.google.com/app/apikey
- View usage statistics
- Check remaining quota
- Set up billing alerts

## Next Steps

1. ✅ Configure API key
2. ✅ Test with sample products
3. ✅ Verify AI insights are specific and detailed
4. ✅ Check buy recommendations make sense
5. 🎯 Start using for real shopping decisions!

## Pro Tips

### Best Products to Scrape
- Products with 20+ reviews
- Recent reviews (last 6 months)
- Detailed reviews (not just star ratings)
- Mixed ratings (3-5 stars) for balanced analysis

### Reading AI Insights
- **Summary** - Quick overview, read first
- **Buy Recommendation** - Final decision aid
- **Pros** - Confirm what you want is there
- **Cons** - Check if deal-breakers exist
- **Target Buyer** - Confirm product matches your needs

### Decision Framework
1. Read Summary
2. Check Buy Recommendation (YES/NO/MAYBE)
3. Review Recommendation Score (8+ is strong)
4. Read Key Considerations
5. Verify Cons are acceptable
6. Confirm you match Target Buyer profile

## Support

### Documentation
- `AI_INSIGHTS_SETUP.md` - Detailed setup guide
- `AI_IMPLEMENTATION_SUMMARY.md` - Technical details

### Common Questions

**Q: Is my data private?**
A: Only public product reviews are sent to Gemini. No personal data.

**Q: How accurate is the AI?**
A: Very reliable for products with 10+ reviews. Based on patterns in actual customer feedback.

**Q: Can I trust the buy recommendation?**
A: Use as guidance, not absolute truth. Always consider your specific needs and budget.

**Q: What if I don't have API key?**
A: System works without AI, just less detailed. Basic analysis still provided.

---

**Ready to start?** Get your API key and experience AI-powered shopping decisions! 🛍️✨
