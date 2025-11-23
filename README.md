---
title: Price Pilot - AI Price Tracker
emoji: 🛍️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
# app_port: 8080
app_port: 7860
---

# 🛍️ Price Pilot - AI-Powered Price Tracker & Review Analyst

An intelligent e-commerce platform that tracks product prices across Amazon, Flipkart, Myntra, and Meesho while providing AI-powered review analysis and insights using Google Gemini.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)

# Working Link 
Live: https://pricepilot-analyst.vercel.app/

## ✨ Features

### 🔍 Multi-Platform Price Tracking
- **Cross-Platform Search**: Find products across Amazon, Flipkart, Myntra, and Meesho
- **Price History Charts**: Visualize price trends with daily/monthly/yearly views
- **Price Alerts**: Get notified when prices drop
- **Best Deal Finder**: Automatically identifies the lowest price across platforms

### 🤖 AI-Powered Analysis (Google Gemini 2.5 Flash)
- **AI Product Insights**: Comprehensive pros, cons, and recommendations
- **Sentiment Analysis Dashboard**: 
  - Overall sentiment distribution (Positive/Neutral/Negative)
  - Key topics from reviews with sentiment scores
  - Controversy, Reliability, and AI Confidence scores
- **Smart Q&A System**: Ask questions about products and get AI-generated answers based on real reviews
- **Auto-Generated Questions**: AI suggests relevant questions from review patterns
- **Intelligent Chatbot**: Context-aware shopping assistant

### 📊 Review Analysis
- **Dynamic Scoring System**:
  - Controversy Score: Based on rating variance
  - Reliability Score: Calculated from review quality, length, and consistency
  - AI Confidence: Data quality and sample size assessment
- **Common Themes Extraction**: Identify recurring patterns in reviews
- **Warning Detection**: Highlights concerns mentioned by users

### 🔐 Authentication
- Email/Password authentication
- Google OAuth integration
- Secure JWT-based sessions

## 🚀 Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: MongoDB
- **Web Scraping**: Scrapy + Playwright
- **AI/ML**: Google Gemini API (2.5 Flash for insights, 2.0 Flash for sentiment)
- **Authentication**: JWT + Google OAuth

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Components**: Radix UI + Tailwind CSS
- **Charts**: Recharts
- **State Management**: React Hooks
- **Routing**: React Router DOM

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- MongoDB installed and running
- Google Gemini API key

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/darksuryansh/PricePilot.git
cd price_tracker
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Install Playwright Browsers
```bash
playwright install
```

#### Configure Environment Variables
Create a `.env` file in the root directory:

```env
# API Keys
RAPIDAPI_KEY=your_rapidapi_key_here

# Google Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=price_tracker

# Authentication Configuration
SECRET_KEY=your-super-secret-key-change-in-production
GOOGLE_CLIENT_ID=your-google-client-id-here
```

**Get Your API Keys:**
- Gemini API: https://makersuite.google.com/app/apikey
- Google OAuth: https://console.cloud.google.com/
- RapidAPI: https://rapidapi.com/

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Start MongoDB
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

## 🎯 Running the Application

### Option 1: Using Batch File (Windows)
```bash
start_app.bat
```

### Option 2: Manual Start

#### Terminal 1 - Backend (Flask)
```bash
python app.py
```
Backend runs on: http://localhost:5000

#### Terminal 2 - Frontend (Vite)
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:5173

## 🕷️ Web Scraping

### Scrape Products from All Platforms
```bash
cd price_scraper

# Amazon
scrapy crawl amazon -a search_query="laptop" -a max_pages=2

# Flipkart
scrapy crawl flipkart -a search_query="laptop" -a max_pages=2

# Myntra
scrapy crawl myntra -a search_query="shoes" -a max_pages=2

# Meesho
scrapy crawl meesho -a search_query="clothes" -a max_pages=2
```

### Automated Daily Scraping
Run the daily scrape batch file:
```bash
daily_scrape.bat
```

## 📁 Project Structure

```
Price_Tracker/
├── app.py                          # Flask backend server
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── daily_scrape.bat               # Automated scraping script
├── start_app.bat                  # Quick start script
│
├── frontend/                      # React frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── ProductComparisonPage.tsx
│   │   │   ├── ReviewInsightsDashboard.tsx
│   │   │   ├── QuestionAnswering.tsx
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.ts           # API integration
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── price_scraper/                 # Scrapy spiders
    ├── price_scraper/
    │   └── spiders/
    │       ├── amazon.py
    │       ├── flipkart.py
    │       ├── myntra.py
    │       └── meesho.py
    └── scrapy.cfg
```

## 🔑 Key API Endpoints

### Products
- `GET /api/products/recent?limit=10` - Get recent products
- `GET /api/products/search?q=laptop` - Search products
- `GET /api/product/<id>` - Get product details
- `GET /api/product/<id>/price-history` - Get price history

### AI Features
- `GET /api/product/<id>/ai-insights` - Get AI analysis (Gemini 2.5 Flash)
- `GET /api/product/<id>/sentiment-analysis` - Get sentiment dashboard (Gemini 2.0 Flash)
- `GET /api/product/<id>/suggested-questions` - Get AI-generated questions
- `POST /api/product/<id>/ask-question` - Ask questions about product
- `POST /api/chatbot` - Chat with AI assistant

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/google-login` - Google OAuth
- `GET /api/auth/user` - Get current user

## 🎨 Features in Detail

### 1. AI Product Insights
Uses Gemini 2.5 Flash to analyze reviews and provide:
- Detailed pros and cons (3-6 each)
- Honest recommendations
- Overall score (1-10)
- Target audience suggestions (3-5 segments)
- Key considerations and warnings

### 2. Sentiment Analysis Dashboard
Powered by Gemini 2.0 Flash:
- **Controversy Score**: Measures rating variance and conflicting opinions
- **Reliability Score**: Based on review length, consistency, and volume
- **AI Confidence**: Data quality assessment
- **Key Topics**: Battery, Build Quality, Camera, Price, Performance, Display
- Color-coded scoring: Green (>70), Orange (30-70), Red (<30)

### 3. Question Answering System
- AI analyzes reviews to suggest relevant questions
- Answers any custom question about the product
- Provides confidence scores and supporting data
- Shows positive percentage, total mentions, common themes
- Highlights warnings from reviews

### 4. Price Tracking
- Real-time price monitoring across platforms
- Historical price charts with trend analysis
- Price drop percentage calculation
- Lowest/highest/average price statistics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Suryansh**
- GitHub: [@darksuryansh](https://github.com/darksuryansh)
- Repository: [PricePilot](https://github.com/darksuryansh/PricePilot)

## 🙏 Acknowledgments

- Google Gemini AI for powerful language models
- Scrapy framework for efficient web scraping
- React and Vite for modern frontend development
- MongoDB for flexible data storage
- Radix UI for accessible components

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation in the `/docs` folder

## If Token limit exced 
phi-3 model run locally and do everything 


## 🚧 Roadmap

- [ ] Email notifications for price drops
- [ ] Mobile app (React Native)
- [ ] More e-commerce platforms
- [ ] Advanced filtering and sorting
- [ ] User wishlists and collections
- [ ] Price prediction using ML
- [ ] Browser extension

---

Made with ❤️ by Suryansh
