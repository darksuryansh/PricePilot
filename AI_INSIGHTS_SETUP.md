# AI Insights Setup Guide

## Getting Your Gemini API Key

The AI-powered product insights feature uses Google's Gemini API to analyze customer reviews and provide intelligent buying recommendations.

### Step 1: Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click on "Get API Key" or "Create API Key"
4. Copy your API key

### Step 2: Configure Your Application

1. Open the `.env` file in the project root directory
2. Find the line: `GEMINI_API_KEY=your_gemini_api_key_here`
3. Replace `your_gemini_api_key_here` with your actual Gemini API key
4. Save the file

Example:
```env
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Restart Your Flask Backend

After updating the `.env` file, restart your Flask server:

```powershell
cd c:\pc\Price_tracker
conda run -n webdev python app.py
```

## Features Powered by Gemini AI

Once configured, the AI will provide:

### 1. **Comprehensive Product Summary**
- Analyzes 15-20 customer reviews
- Provides 2-3 sentence overview of customer sentiment
- Highlights key value propositions

### 2. **Pros & Cons Analysis**
- Extracts 4-6 specific positive aspects
- Identifies 3-5 concerns or drawbacks
- Based on real customer feedback

### 3. **AI Recommendation Score**
- 1-10 rating based on quality, value, and satisfaction
- Color-coded badges (green for high, yellow for medium, red for low)

### 4. **Buy/Don't Buy Recommendation**
- Clear YES/NO/MAYBE recommendation
- 2-3 sentence reasoning explaining the recommendation
- Considers price, quality, reviews, and value for money

### 5. **Target Buyer Profile**
- Identifies who the product is best suited for
- Examples: "budget-conscious buyers", "professionals", "students"

### 6. **Key Considerations**
- 2-3 important factors to consider before purchasing
- Helps with informed decision-making

## How It Works

1. When you scrape a product, reviews are automatically collected
2. Navigate to the product comparison page
3. The AI Insights tab automatically loads (may take 5-10 seconds)
4. AI analyzes the reviews and generates insights
5. Results are displayed in an easy-to-read format

## Fallback Mode

If the Gemini API key is not configured or unavailable:
- The system will use basic analysis
- Insights will still be generated but less detailed
- You'll see a note that AI analysis is pending

## API Usage Notes

- **Free Tier**: Gemini API offers a generous free tier
- **Rate Limits**: 60 requests per minute for free tier
- **Token Limits**: Each request uses tokens based on review length
- **Cost**: Free up to certain limits, then pay-as-you-go pricing

## Troubleshooting

### AI Insights Not Loading?

1. **Check API Key**: Ensure your Gemini API key is correctly set in `.env`
2. **Check Console**: Look for error messages in the Flask terminal
3. **Restart Backend**: After changing `.env`, restart Flask
4. **Check Reviews**: Product needs customer reviews for AI analysis

### Error Messages

- `"Gemini API key not configured"` - Add your API key to `.env`
- `"No review texts available"` - Product doesn't have enough reviews
- `"AI insights not available yet"` - Wait a few seconds for generation

### Testing AI Insights

1. Scrape a product with many reviews (preferably 10+ reviews)
2. Go to the product comparison page
3. Check the "Summary" tab under "AI Product Insights"
4. You should see the "Should I Buy This?" card with AI recommendation

## Privacy & Data

- Reviews are sent to Google's Gemini API for analysis
- Only product name, price, rating, and review text are sent
- No personal user data is transmitted
- Data is used only for generating insights

## Support

If you encounter issues:
1. Check the Flask terminal for error messages
2. Verify your API key is valid on [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Ensure you have internet connectivity
4. Check if Gemini API is experiencing outages

---

**Note**: The AI insights feature requires an active internet connection and a valid Gemini API key to function.
