import { useState } from "react";
import { ThemeProvider } from "./components/ThemeProvider";
import { AnimatedBackground } from "./components/AnimatedBackground";
import { Navbar } from "./components/Navbar";
import { Hero } from "./components/Hero";
import { HowItWorks } from "./components/HowItWorks";
import { TrendingComparisons } from "./components/TrendingComparisons";
import { SearchResults } from "./components/SearchResults";
import { ProductComparisonPage } from "./components/ProductComparisonPage";
import { LoadingState } from "./components/LoadingState";
import { LoginPage } from "./components/LoginPage";
import { WatchlistPage } from "./components/WatchlistPage";
import { PriceComparisonPage } from "./components/PriceComparisonPage";
import { ChatbotFAB } from "./components/ChatbotFAB";
import { Footer } from "./components/Footer";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import * as api from "./services/api";

// Mock product database
const mockProducts = {
  "iphone 15 pro": {
    name: "Apple iPhone 15 Pro (128GB) - Natural Titanium",
    description: "The iPhone 15 Pro features a strong and light aerospace-grade titanium design with a textured matte glass back. It has the new A17 Pro chip for incredible performance and amazing battery life. Advanced camera system with 48MP Main camera for super-high-resolution photos.",
    image: "https://images.unsplash.com/photo-1699265837122-7636e128b4b0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWFydHBob25lJTIwcHJvZHVjdHxlbnwxfHx8fDE3NjIwNjA4Nzd8MA&ixlib=rb-4.1.0&q=80&w=1080",
    platforms: {
      amazon: {
        price: 129900,
        originalPrice: 134900,
        rating: 4.5,
        reviews: 12453,
        link: "https://amazon.in",
        availability: true
      },
      myntra: {
        price: 132900,
        originalPrice: 134900,
        rating: 4.3,
        reviews: 3241,
        link: "https://myntra.com",
        availability: true
      },
      flipkart: {
        price: 131900,
        originalPrice: 134900,
        rating: 4.4,
        reviews: 8967,
        link: "https://flipkart.com",
        availability: true
      }
    },
    features: [
      { name: "Display", value: "6.1-inch Super Retina XDR display" },
      { name: "Processor", value: "A17 Pro chip with 6-core CPU" },
      { name: "Camera", value: "48MP Main | Ultra Wide | Telephoto" },
      { name: "Battery", value: "Up to 23 hours video playback" },
      { name: "Material", value: "Titanium design with Ceramic Shield" },
      { name: "Storage", value: "128GB" },
      { name: "5G", value: "5G capable" },
      { name: "Water Resistant", value: "IP68 rating" }
    ],
    aiInsights: {
      insights: "The iPhone 15 Pro represents a significant upgrade with its titanium design and A17 Pro chip. Based on analysis of over 24,000 reviews across platforms, users are particularly impressed with the camera quality, battery life, and the new Action button. The price difference across platforms is minimal, with Amazon offering the best deal currently.",
      pros: [
        "Premium titanium build quality",
        "Exceptional camera performance",
        "A17 Pro chip delivers outstanding performance",
        "Excellent battery life",
        "Beautiful display with always-on capability"
      ],
      cons: [
        "High price point compared to competitors",
        "No significant design changes from iPhone 14 Pro",
        "USB-C cable limited to USB 2.0 speeds on base model",
        "Heating issues reported during intensive tasks"
      ],
      recommendation: "Highly recommended if you're upgrading from iPhone 12 or older. The titanium design feels premium and the camera improvements are noticeable. Amazon currently offers the best price with fastest delivery.",
      recommendationScore: 8.5
    },
    priceHistory: {
      daily: [
        { date: "Oct 26", amazon: 130900, myntra: 133900, flipkart: 132900 },
        { date: "Oct 27", amazon: 130500, myntra: 133500, flipkart: 132500 },
        { date: "Oct 28", amazon: 131200, myntra: 133200, flipkart: 132200 },
        { date: "Oct 29", amazon: 130800, myntra: 132900, flipkart: 131900 },
        { date: "Oct 30", amazon: 130200, myntra: 132900, flipkart: 131900 },
        { date: "Oct 31", amazon: 129900, myntra: 132900, flipkart: 131900 },
        { date: "Nov 1", amazon: 129900, myntra: 132900, flipkart: 131900 }
      ],
      monthly: [
        { month: "May", amazon: 134900, myntra: 134900, flipkart: 134900 },
        { month: "Jun", amazon: 133900, myntra: 134900, flipkart: 134500 },
        { month: "Jul", amazon: 132900, myntra: 134200, flipkart: 133900 },
        { month: "Aug", amazon: 131900, myntra: 133500, flipkart: 132900 },
        { month: "Sep", amazon: 130900, myntra: 133000, flipkart: 132200 },
        { month: "Oct", amazon: 129900, myntra: 132900, flipkart: 131900 }
      ],
      yearly: [
        { year: "2023", amazon: 134900, myntra: 134900, flipkart: 134900 },
        { year: "2024", amazon: 129900, myntra: 132900, flipkart: 131900 }
      ]
    }
  },
  "macbook air m2": {
    name: "Apple MacBook Air M2 Chip (13-inch, 8GB RAM, 256GB SSD)",
    description: "The redesigned MacBook Air with M2 chip is incredibly thin and light. It features a stunning Liquid Retina display, advanced camera and audio, and all-day battery life. The M2 chip delivers exceptional performance and incredible battery life.",
    image: "https://images.unsplash.com/photo-1511385348-a52b4a160dc2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsYXB0b3AlMjBjb21wdXRlcnxlbnwxfHx8fDE3NjIwNDkzMDh8MA&ixlib=rb-4.1.0&q=80&w=1080",
    platforms: {
      amazon: {
        price: 99900,
        originalPrice: 119900,
        rating: 4.6,
        reviews: 8234,
        link: "https://amazon.in",
        availability: true
      },
      myntra: {
        price: 104900,
        originalPrice: 119900,
        rating: 4.4,
        reviews: 1523,
        link: "https://myntra.com",
        availability: true
      },
      flipkart: {
        price: 101900,
        originalPrice: 119900,
        rating: 4.5,
        reviews: 5678,
        link: "https://flipkart.com",
        availability: true
      }
    },
    features: [
      { name: "Display", value: "13.6-inch Liquid Retina display" },
      { name: "Processor", value: "Apple M2 chip with 8-core CPU" },
      { name: "Memory", value: "8GB unified memory" },
      { name: "Storage", value: "256GB SSD" },
      { name: "Battery", value: "Up to 18 hours battery life" },
      { name: "Weight", value: "1.24 kg" },
      { name: "Camera", value: "1080p FaceTime HD camera" },
      { name: "Audio", value: "Four-speaker sound system" }
    ],
    aiInsights: {
      insights: "The MacBook Air M2 is a remarkable laptop that balances performance, portability, and battery life exceptionally well. Analysis of 15,457 reviews shows users love the silent operation, incredible battery life, and the beautiful display.",
      pros: [
        "Excellent M2 chip performance",
        "All-day battery life (15-18 hours)",
        "Completely silent operation (no fans)",
        "Beautiful Liquid Retina display",
        "Lightweight and portable design"
      ],
      cons: [
        "Only 256GB base storage",
        "Limited to 8GB RAM in base model",
        "Only two USB-C ports",
        "No SD card slot",
        "Price premium over Windows alternatives"
      ],
      recommendation: "Excellent choice for students and professionals who need a reliable, portable laptop. Amazon offers the best price with significant savings.",
      recommendationScore: 9.0
    },
    priceHistory: {
      daily: [
        { date: "Oct 26", amazon: 101900, myntra: 105900, flipkart: 103900 },
        { date: "Oct 27", amazon: 101500, myntra: 105500, flipkart: 103500 },
        { date: "Oct 28", amazon: 100900, myntra: 105200, flipkart: 102900 },
        { date: "Oct 29", amazon: 100500, myntra: 104900, flipkart: 102500 },
        { date: "Oct 30", amazon: 100200, myntra: 104900, flipkart: 102200 },
        { date: "Oct 31", amazon: 99900, myntra: 104900, flipkart: 101900 },
        { date: "Nov 1", amazon: 99900, myntra: 104900, flipkart: 101900 }
      ],
      monthly: [
        { month: "May", amazon: 119900, myntra: 119900, flipkart: 119900 },
        { month: "Jun", amazon: 115900, myntra: 119900, flipkart: 117900 },
        { month: "Jul", amazon: 110900, myntra: 114900, flipkart: 112900 },
        { month: "Aug", amazon: 106900, myntra: 109900, flipkart: 107900 },
        { month: "Sep", amazon: 102900, myntra: 106900, flipkart: 104900 },
        { month: "Oct", amazon: 99900, myntra: 104900, flipkart: 101900 }
      ],
      yearly: [
        { year: "2023", amazon: 119900, myntra: 119900, flipkart: 119900 },
        { year: "2024", amazon: 99900, myntra: 104900, flipkart: 101900 }
      ]
    }
  }
};

type Page = 'home' | 'search-results' | 'product' | 'login' | 'watchlist' | 'compare-prices';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentProduct, setCurrentProduct] = useState<any>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchType, setSearchType] = useState<'name' | 'link'>('name');

  const handleSearch = async (query: string, type: 'name' | 'link' = 'name') => {
    setSearchQuery(query);
    setSearchType(type);
    setLoading(true);

    try {
      if (type === 'link') {
        // If it's a URL, scrape it first then go directly to product page
        toast.info('Scraping product from URL...', { duration: 3000 });
        const scrapeResult = await api.scrapeProduct(query);
        
        if (scrapeResult.success && scrapeResult.product_id) {
          toast.success('Product scraped successfully!');
          
          // Fetch the scraped product details
          const product = await api.getProduct(scrapeResult.product_id);
          
          // If cross-platform matches were found, fetch those too
          if (scrapeResult.cross_platform_matches && scrapeResult.cross_platform_matches.length > 0) {
            toast.info('Finding cross-platform prices...', { duration: 2000 });
            
            // Fetch details for all cross-platform products
            const crossPlatformProducts = await Promise.all(
              scrapeResult.cross_platform_matches.map(async (match: any) => {
                try {
                  const crossProduct = await api.getProduct(match.product_id);
                  return crossProduct;
                } catch (error) {
                  console.error(`Failed to fetch ${match.platform} product:`, error);
                  return null;
                }
              })
            );
            
            // Filter out failed fetches and add to product
            const validCrossPlatformProducts = crossPlatformProducts.filter(p => p !== null);
            product.crossPlatformProducts = validCrossPlatformProducts;
            
            if (validCrossPlatformProducts.length > 0) {
              toast.success(`Found prices on ${validCrossPlatformProducts.length + 1} platforms!`);
            }
          }
          
          setCurrentProduct(product);
          setCurrentPage('product');
        } else {
          toast.error('Failed to scrape product');
          setCurrentPage('search-results');
          setSearchResults([]);
        }
      } else {
        // Search by name - show search results
        setCurrentPage('search-results');
        const products = await api.searchProducts(query);
        if (products.length === 0) {
          toast.info('No products found. Try a different search term.');
        }
        setSearchResults(products);
      }
    } catch (error: any) {
      console.error('Search error:', error);
      toast.error(error.message || 'Failed to search products');
      setCurrentPage('search-results');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleProductSelect = async (productId: string) => {
    setLoading(true);
    setCurrentPage('product');

    try {
      const product = await api.getProduct(productId);
      setCurrentProduct(product);
    } catch (error: any) {
      console.error('Product fetch error:', error);
      toast.error(error.message || 'Failed to load product');
      setCurrentProduct(null);
    } finally {
      setLoading(false);
    }
  };

  const handleNavigate = (page: string) => {
    if (page === 'home') {
      setCurrentPage('home');
      setCurrentProduct(null);
      setSearchQuery('');
    } else if (page === 'login') {
      setCurrentPage('login');
    } else if (page === 'watchlist') {
      if (isLoggedIn) {
        setCurrentPage('watchlist');
      } else {
        setCurrentPage('login');
      }
    } else if (page === 'compare-prices') {
      setCurrentPage('compare-prices');
    }
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
    setCurrentPage('watchlist');
  };

  return (
    <ThemeProvider>
    <div className="min-h-screen bg-background transition-colors duration-300">
      {/* Animated Background */}
      <AnimatedBackground />
      
      {/* Navbar */}
      <Navbar 
        onNavigate={handleNavigate}
        onSearch={handleSearch}
        isLoggedIn={isLoggedIn}
      />

      {/* Main Content */}
      {loading ? (
        <LoadingState />
      ) : (
        <>
          {currentPage === 'home' && (
            <>
              <Hero onSearch={handleSearch} />
              <HowItWorks />
              <TrendingComparisons onProductClick={handleProductSelect} />
            </>
          )}

          {currentPage === 'search-results' && (
            <SearchResults 
              searchQuery={searchQuery}
              onProductSelect={handleProductSelect}
              products={searchResults}
            />
          )}

          {currentPage === 'product' && currentProduct && (
            <ProductComparisonPage product={currentProduct} />
          )}

          {currentPage === 'login' && (
            <LoginPage 
              onLogin={handleLogin}
              onNavigate={handleNavigate}
            />
          )}

          {currentPage === 'watchlist' && isLoggedIn && (
            <WatchlistPage onProductClick={handleProductSelect} />
          )}

          {currentPage === 'compare-prices' && (
            <PriceComparisonPage onNavigate={handleNavigate} />
          )}
        </>
      )}

      {/* Chatbot FAB */}
      <ChatbotFAB 
        productName={currentProduct?.name} 
        productId={currentProduct?.asin || currentProduct?.product_id || currentProduct?._id}
      />

      {/* Toast Notifications */}
      <Toaster />

      {/* Footer */}
      <Footer />
    </div>
    </ThemeProvider>
  );
}
