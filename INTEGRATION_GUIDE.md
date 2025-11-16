# Backend-Frontend Integration Guide

## Overview
Your React frontend is now integrated with your Flask backend for scraping e-commerce websites.

## Features Integrated
- ✅ Scrape products from Amazon, Flipkart, and Myntra by URL
- ✅ Search products by name from your database
- ✅ View product details
- ✅ Real-time toast notifications for user feedback

## How to Run

### 1. Start the Flask Backend
```powershell
# Make sure you're in the project root
cd C:\pc\Price_tracker

# Activate your conda environment
conda activate webdev

# Run the Flask app
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Start the React Frontend
```powershell
# Open a new terminal and navigate to frontend
cd C:\pc\Price_tracker\frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:5173` (or similar)

## Usage

### Search by URL
1. Click on "Search by URL" tab in the search bar
2. Paste a product URL from Amazon, Flipkart, or Myntra
3. Click Search - the backend will scrape the product
4. View the scraped product details

### Search by Name
1. Use the "Search by Name" tab (default)
2. Enter a product name (e.g., "iPhone 15")
3. View results from your database

## API Endpoints Being Used

- `POST /api/scrape` - Scrape a product from URL
- `GET /api/product/:id` - Get product details
- `GET /api/products/search` - Search products by name
- `GET /api/product/:id/price-history` - Get price history
- `GET /api/product/:id/reviews` - Get product reviews
- `GET /api/product/:id/ai-insights` - Get AI-powered insights

## Configuration

The frontend API URL is configured in `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:5000
```

If you deploy your backend to a different URL, update this file.

## Troubleshooting

### CORS Issues
The Flask backend is already configured with CORS for localhost ports 3000, 3001, 5173, 5174.

### Backend Not Responding
1. Make sure Flask app is running: `python app.py`
2. Check the console for errors
3. Verify MongoDB is running

### Scraping Fails
1. Check if the URL is from a supported platform (Amazon, Flipkart, Myntra)
2. Look at the Flask console for detailed error messages
3. The scraping process may take 30-60 seconds

## Notes

- AI insights feature is ready but requires Gemini API key in your backend `.env`
- Price history and reviews will be populated as you scrape more products over time
- The first scrape of a product may take longer
