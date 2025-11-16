import { ImageWithFallback } from "./figma/ImageWithFallback";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Badge } from "./ui/badge";
import { Sparkles, ThumbsUp, ThumbsDown, TrendingUp, TrendingDown, CheckCircle2, Info, Star, Award, Zap, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { PriceTable } from "./PriceTable";
import { PriceHistoryChart } from "./PriceHistoryChart";
import { ReviewInsightsDashboard } from "./ReviewInsightsDashboard";
import { QuestionAnswering } from "./QuestionAnswering";
import { Button } from "./ui/button";
import { Progress } from "./ui/progress";
import { useState, useEffect } from "react";
import * as api from "../services/api";
import { toast } from "sonner";

interface ProductComparisonPageProps {
  product: any;
}

export function ProductComparisonPage({ product }: ProductComparisonPageProps) {
  const [priceView, setPriceView] = useState<'daily' | 'monthly' | 'yearly'>('daily');
  const [activeInsightTab, setActiveInsightTab] = useState('summary');
  const [loading, setLoading] = useState(true);
  const [priceHistory, setPriceHistory] = useState<any>(null);
  const [aiInsights, setAIInsights] = useState<any>(null);
  const [sentimentData, setSentimentData] = useState<any>(null);
  const [sentimentLoading, setSentimentLoading] = useState(false);

  // Load additional data when component mounts
  useEffect(() => {
    const loadProductData = async () => {
      if (!product) return;

      try {
        setLoading(true);
        const productId = product.asin || product.product_id || product._id;

        // Load price history
        const historyData = await api.getPriceHistory(productId, 'daily', 30);
        setPriceHistory(historyData);

        // Try to load AI insights (optional, may fail if not generated yet)
        try {
          const insights: any = await api.getAIInsights(productId);
          console.log('🤖 Raw AI insights received:', insights);
          // Normalize snake_case to camelCase for consistent access
          const normalizedInsights = {
            ...insights,
            recommendationScore: insights.recommendation_score || insights.recommendationScore || 7,
            buyRecommendation: insights.buy_recommendation || insights.buyRecommendation,
            targetBuyer: insights.target_buyer || insights.targetBuyer,
            keyConsiderations: insights.key_considerations || insights.keyConsiderations,
            totalReviewsAnalyzed: insights.total_reviews_analyzed || insights.totalReviewsAnalyzed,
            averageRating: insights.average_rating || insights.averageRating,
            aiGenerated: insights.ai_generated || insights.aiGenerated
          };
          console.log('✨ Normalized AI insights:', normalizedInsights);
          console.log('📊 Recommendation Score:', normalizedInsights.recommendationScore);
          setAIInsights(normalizedInsights);
        } catch (error) {
          console.log('AI insights not available yet');
        }

        // Load sentiment analysis (optional)
        try {
          setSentimentLoading(true);
          const sentiment = await api.getSentimentAnalysis(productId);
          console.log('📊 Sentiment analysis received:', sentiment);
          setSentimentData(sentiment);
        } catch (error: any) {
          console.error('❌ Sentiment analysis error:', error.message);
          // Set empty sentiment data to show dashboard with message
          setSentimentData({
            error: error.message,
            overall_sentiment: { positive: 0, neutral: 0, negative: 0 },
            key_topics: [],
            controversy_score: 0,
            reliability_score: 0,
            ai_confidence: 0
          });
        } finally {
          setSentimentLoading(false);
        }

      } catch (error: any) {
        console.error('Error loading product data:', error);
        toast.error('Failed to load some product data');
      } finally {
        setLoading(false);
      }
    };

    loadProductData();
  }, [product]);

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading product...</p>
        </div>
      </div>
    );
  }

  // Debug: Log product data
  console.log('Product data received:', product);

  // Build platforms object from main product and cross-platform products
  const buildPlatformsData = () => {
    const platforms: any = {
      amazon: { price: 0, originalPrice: 0, rating: 0, reviews: 0, link: '#', availability: false },
      flipkart: { price: 0, originalPrice: 0, rating: 0, reviews: 0, link: '#', availability: false },
      myntra: { price: 0, originalPrice: 0, rating: 0, reviews: 0, link: '#', availability: false },
      meesho: { price: 0, originalPrice: 0, rating: 0, reviews: 0, link: '#', availability: false }
    };

    // Add main product
    const mainPlatform = product.platform?.toLowerCase();
    if (mainPlatform && platforms[mainPlatform]) {
      platforms[mainPlatform] = {
        price: product.current_price || 0,
        originalPrice: product.original_price || product.current_price || 0,
        rating: product.rating || 0,
        reviews: product.reviews_count || 0,
        link: product.url || '#',
        availability: true
      };
    }

    // Add cross-platform products
    if (product.crossPlatformProducts && Array.isArray(product.crossPlatformProducts)) {
      product.crossPlatformProducts.forEach((crossProduct: any) => {
        const crossPlatform = crossProduct.platform?.toLowerCase();
        if (crossPlatform && platforms[crossPlatform]) {
          platforms[crossPlatform] = {
            price: crossProduct.current_price || 0,
            originalPrice: crossProduct.original_price || crossProduct.current_price || 0,
            rating: crossProduct.rating || 0,
            reviews: crossProduct.reviews_count || 0,
            link: crossProduct.url || '#',
            availability: true
          };
        }
      });
    }

    return platforms;
  };

  // Transform API product data into display format
  const displayProduct = {
    name: product.name || product.title || 'Product Name Not Available',
    description: product.description || product.product_description || 'No description available',
    image: product.image || product.image_url || (product.images && product.images[0]) || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
    platforms: buildPlatformsData(),
    features: Array.isArray(product.features) && product.features.length > 0
      ? product.features.map((f: any) => {
          if (typeof f === 'object' && !Array.isArray(f)) {
            const key = Object.keys(f)[0];
            return { name: key, value: String(f[key]) };
          }
          return f;
        })
      : product.specifications && typeof product.specifications === 'object' && Object.keys(product.specifications).length > 0
        ? Object.entries(product.specifications).map(([key, value]) => ({
            name: key,
            value: String(value)
          }))
        : [
            { name: 'Platform', value: product.platform || 'Unknown' },
            { name: 'Price', value: `₹${product.current_price?.toLocaleString() || '0'}` },
            { name: 'Rating', value: product.rating ? `${product.rating}/5` : 'N/A' },
            { name: 'Availability', value: 'In Stock' },
          ],
    aiInsights: aiInsights || {
      insights: `This product has been scraped from ${product.platform || 'the platform'}. AI insights will be available after analyzing reviews.`,
      pros: [
        'Competitive pricing',
        'Available on major platforms',
        'Customer reviews available'
      ],
      cons: [
        'AI analysis pending',
        'Limited historical data'
      ],
      recommendation: 'This is a newly tracked product. Check back later for detailed AI-powered insights.',
      recommendationScore: 7,
      buyRecommendation: 'MAYBE',
      targetBuyer: 'General consumers',
      keyConsiderations: ['Check product reviews', 'Compare prices', 'Verify specifications'],
      aiGenerated: false
    },
    priceHistory: priceHistory && priceHistory.history && priceHistory.history.length > 0 ? {
      daily: priceHistory.history.slice(-7).map((h: any) => ({
        date: new Date(h.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        amazon: h.amazon || null,
        flipkart: h.flipkart || null,
        myntra: h.myntra || null
      })),
      monthly: priceHistory.history.slice(-30).map((h: any) => ({
        date: new Date(h.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        amazon: h.amazon || null,
        flipkart: h.flipkart || null,
        myntra: h.myntra || null
      })),
      yearly: priceHistory.history.map((h: any) => ({
        date: new Date(h.date).toLocaleDateString('en-US', { month: 'short' }),
        amazon: h.amazon || null,
        flipkart: h.flipkart || null,
        myntra: h.myntra || null
      }))
    } : (() => {
      // Fallback: Use current prices from all platforms
      const currentPrices: any = {
        date: 'Today',
        amazon: null,
        flipkart: null,
        myntra: null
      };
      
      // Add main product price
      if (product.platform && product.current_price) {
        currentPrices[product.platform.toLowerCase()] = product.current_price;
      }
      
      // Add cross-platform products prices
      if (product.crossPlatformProducts && Array.isArray(product.crossPlatformProducts)) {
        product.crossPlatformProducts.forEach((crossProduct: any) => {
          if (crossProduct.platform && crossProduct.current_price) {
            currentPrices[crossProduct.platform.toLowerCase()] = crossProduct.current_price;
          }
        });
      }
      
      return {
        daily: [currentPrices],
        monthly: [{ ...currentPrices, date: 'This Month' }],
        yearly: [{ ...currentPrices, date: 'This Year' }]
      };
    })()
  };

  // Debug: Log transformed product
  console.log('Transformed displayProduct:', displayProduct);

  // Show loading while fetching additional data
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30 dark:from-gray-900 dark:via-blue-950/30 dark:to-purple-950/30">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400 text-lg">Loading product details...</p>
          <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">Fetching price history and insights</p>
        </div>
      </div>
    );
  }

  const getPriceStats = () => {
    const prices = [
      { price: displayProduct.platforms.amazon.price, platform: 'Amazon' },
      { price: displayProduct.platforms.myntra.price, platform: 'Myntra' },
      { price: displayProduct.platforms.flipkart.price, platform: 'Flipkart' },
      { price: displayProduct.platforms.meesho?.price, platform: 'Meesho' }
    ].filter(p => p.price && p.price > 0);

    if (prices.length === 0) {
      return {
        lowestPrice: product.current_price,
        lowestPlatform: product.platform,
        highestPrice: product.current_price,
        highestPlatform: product.platform,
        averagePrice: product.current_price
      };
    }

    const sorted = [...prices].sort((a, b) => a.price - b.price);
    const avg = Math.round(prices.reduce((sum, p) => sum + p.price, 0) / prices.length);

    return {
      lowestPrice: sorted[0].price,
      lowestPlatform: sorted[0].platform,
      highestPrice: sorted[sorted.length - 1].price,
      highestPlatform: sorted[sorted.length - 1].platform,
      averagePrice: avg
    };
  };

  const stats = getPriceStats();

  // Calculate aggregate ratings
  const platformsWithData = [
    displayProduct.platforms.amazon,
    displayProduct.platforms.flipkart,
    displayProduct.platforms.myntra,
    displayProduct.platforms.meesho
  ].filter(p => p && p.rating > 0 && p.reviews > 0);

  const aggregateRating = platformsWithData.length > 0
    ? (
      platformsWithData.reduce((sum, p) => sum + (p.rating * p.reviews), 0) /
      platformsWithData.reduce((sum, p) => sum + p.reviews, 0)
    ).toFixed(1)
    : product.rating?.toFixed(1) || '0.0';

  const totalReviews = platformsWithData.reduce((sum, p) => sum + p.reviews, 0) || product.reviews_count || 0;

  // Mock rating breakdown
  const ratingBreakdown = [
    { stars: 5, percentage: 65, count: Math.round(totalReviews * 0.65) },
    { stars: 4, percentage: 20, count: Math.round(totalReviews * 0.20) },
    { stars: 3, percentage: 10, count: Math.round(totalReviews * 0.10) },
    { stars: 2, percentage: 3, count: Math.round(totalReviews * 0.03) },
    { stars: 1, percentage: 2, count: Math.round(totalReviews * 0.02) }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30 dark:from-gray-900 dark:via-blue-950/30 dark:to-purple-950/30 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 bg-pattern-dots opacity-50 pointer-events-none" />
      <div className="absolute top-20 right-20 w-72 h-72 bg-blue-500/10 dark:bg-blue-500/20 rounded-full blur-3xl animate-float pointer-events-none" />
      <div className="absolute bottom-20 left-20 w-96 h-96 bg-purple-500/10 dark:bg-purple-500/20 rounded-full blur-3xl animate-float pointer-events-none" style={{ animationDelay: '2s' }} />

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8 relative z-10">
        {/* Product Header Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fadeIn">
          {/* Left: Product Images */}
          <div className="space-y-4">
            <div className="group bg-white dark:bg-gray-800 rounded-3xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-2xl hover:shadow-blue-500/20 dark:hover:shadow-blue-500/40 transition-all duration-500 animate-card-reveal">
              <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-800 relative overflow-hidden">
                <ImageWithFallback
                  src={displayProduct.image}
                  alt={displayProduct.name}
                  className="w-full h-full object-contain p-8 group-hover:scale-105 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
              </div>
            </div>
            <div className="grid grid-cols-4 gap-3">
              {[1, 2, 3, 4].map((i) => (
                <button 
                  key={i} 
                  className="aspect-square bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-300 group overflow-hidden hover:scale-105 animate-fadeIn"
                  style={{ animationDelay: `${i * 0.1}s` }}
                >
                  <ImageWithFallback
                    src={displayProduct.image}
                    alt={`${displayProduct.name} view ${i}`}
                    className="w-full h-full object-contain p-2 group-hover:scale-110 transition-transform duration-300"
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Right: Product Info & AI Insights */}
          <div className="space-y-6">
            <div className="animate-card-reveal stagger-1">
              <h1 className="text-3xl md:text-4xl text-gray-900 dark:text-white mb-2">{displayProduct.name}</h1>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{displayProduct.description}</p>
            </div>

            {/* AI-Powered Insights Card with new tab structure */}
            <Card className="border-2 border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50/50 via-blue-50/50 to-white dark:from-purple-950/30 dark:via-blue-950/30 dark:to-gray-800 shadow-xl hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-500 animate-card-reveal stagger-2 overflow-hidden relative">
              {/* Animated background decoration */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-500/10 to-blue-500/10 rounded-full blur-3xl animate-pulse pointer-events-none" />
              
              <CardHeader className="relative z-10">
                <CardTitle className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl animate-float shadow-lg">
                    <Sparkles className="h-5 w-5 text-white" />
                  </div>
                  <span className="gradient-text">AI Product Insights</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="relative z-10">
                <Tabs value={activeInsightTab} onValueChange={setActiveInsightTab} className="w-full">
                  <TabsList className="grid w-full grid-cols-5 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm p-1 rounded-xl border border-purple-200 dark:border-purple-800">
                    <TabsTrigger 
                      value="summary" 
                      className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600 data-[state=active]:text-white rounded-lg transition-all duration-300 data-[state=active]:shadow-lg"
                    >
                      <Zap className="h-3 w-3 mr-1" />
                      Summary
                    </TabsTrigger>
                    <TabsTrigger 
                      value="pros" 
                      className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-600 data-[state=active]:to-emerald-600 data-[state=active]:text-white rounded-lg transition-all duration-300 data-[state=active]:shadow-lg"
                    >
                      <ThumbsUp className="h-3 w-3 mr-1" />
                      Pros
                    </TabsTrigger>
                    <TabsTrigger 
                      value="cons" 
                      className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-red-600 data-[state=active]:to-orange-600 data-[state=active]:text-white rounded-lg transition-all duration-300 data-[state=active]:shadow-lg"
                    >
                      <ThumbsDown className="h-3 w-3 mr-1" />
                      Cons
                    </TabsTrigger>
                    <TabsTrigger 
                      value="features" 
                      className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-indigo-600 data-[state=active]:text-white rounded-lg transition-all duration-300 data-[state=active]:shadow-lg"
                    >
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      Features
                    </TabsTrigger>
                    <TabsTrigger 
                      value="ratings" 
                      className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-yellow-600 data-[state=active]:to-amber-600 data-[state=active]:text-white rounded-lg transition-all duration-300 data-[state=active]:shadow-lg"
                    >
                      <Star className="h-3 w-3 mr-1" />
                      Ratings
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="summary" className="mt-6 space-y-4 animate-fadeIn">
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                      {displayProduct.aiInsights.insights}
                    </p>
                    
                    {/* Buy Recommendation Card */}
                    {displayProduct.aiInsights.buyRecommendation && (
                      <div className={`p-4 rounded-xl border-2 ${
                        displayProduct.aiInsights.buyRecommendation === 'YES' 
                          ? 'bg-green-50/80 dark:bg-green-900/20 border-green-500' 
                          : displayProduct.aiInsights.buyRecommendation === 'NO'
                          ? 'bg-red-50/80 dark:bg-red-900/20 border-red-500'
                          : 'bg-yellow-50/80 dark:bg-yellow-900/20 border-yellow-500'
                      } backdrop-blur-sm`}>
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${
                            displayProduct.aiInsights.buyRecommendation === 'YES' 
                              ? 'bg-green-500' 
                              : displayProduct.aiInsights.buyRecommendation === 'NO'
                              ? 'bg-red-500'
                              : 'bg-yellow-500'
                          }`}>
                            {displayProduct.aiInsights.buyRecommendation === 'YES' ? (
                              <ThumbsUp className="h-4 w-4 text-white" />
                            ) : (
                              <ThumbsDown className="h-4 w-4 text-white" />
                            )}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold text-sm mb-1 text-gray-900 dark:text-white">
                              Should I Buy This? <span className={`${
                                displayProduct.aiInsights.buyRecommendation === 'YES' 
                                  ? 'text-green-600 dark:text-green-400' 
                                  : displayProduct.aiInsights.buyRecommendation === 'NO'
                                  ? 'text-red-600 dark:text-red-400'
                                  : 'text-yellow-600 dark:text-yellow-400'
                              }`}>{displayProduct.aiInsights.buyRecommendation}</span>
                            </h4>
                            <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                              {displayProduct.aiInsights.recommendation}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center gap-3 pt-2 flex-wrap">
                      <span className="text-sm text-gray-700 dark:text-gray-300">AI Recommendation Score:</span>
                      <Badge 
                        className={`${
                          displayProduct.aiInsights.recommendationScore >= 8 ? 'bg-gradient-to-r from-green-600 to-emerald-600' :
                          displayProduct.aiInsights.recommendationScore >= 6 ? 'bg-gradient-to-r from-yellow-600 to-orange-600' :
                          'bg-gradient-to-r from-red-600 to-rose-600'
                        } text-white shadow-lg hover:scale-110 transition-transform duration-300`}
                      >
                        <Award className="h-3 w-3 mr-1" />
                        {displayProduct.aiInsights.recommendationScore}/10
                      </Badge>
                      {displayProduct.aiInsights.aiGenerated && (
                        <Badge className="bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">
                          <Sparkles className="h-3 w-3 mr-1" />
                          AI Generated
                        </Badge>
                      )}
                    </div>
                    
                    {/* Target Buyer & Key Considerations */}
                    {displayProduct.aiInsights.targetBuyer && (
                      <div className="p-3 bg-blue-50/50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          <span className="font-semibold text-blue-600 dark:text-blue-400">Best for:</span> {displayProduct.aiInsights.targetBuyer}
                        </p>
                      </div>
                    )}
                    
                    {displayProduct.aiInsights.keyConsiderations && displayProduct.aiInsights.keyConsiderations.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300">Key Considerations:</h4>
                        <ul className="space-y-1">
                          {displayProduct.aiInsights.keyConsiderations.map((consideration: string, index: number) => (
                            <li key={index} className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-400">
                              <span className="text-purple-600 dark:text-purple-400">•</span>
                              {consideration}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="pros" className="mt-6 animate-fadeIn">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg">
                          <ThumbsUp className="h-4 w-4 text-white" />
                        </div>
                        <span className="text-green-600 dark:text-green-400">What Users Love</span>
                      </div>
                      <ul className="space-y-2">
                        {displayProduct.aiInsights.pros.map((pro: string, index: number) => (
                          <li 
                            key={index} 
                            className="flex items-start gap-3 p-3 bg-green-50/50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800 hover:scale-105 transition-all duration-300 animate-fadeIn"
                            style={{ animationDelay: `${index * 0.1}s` }}
                          >
                            <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-700 dark:text-gray-300">{pro}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </TabsContent>

                  <TabsContent value="cons" className="mt-6 animate-fadeIn">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="p-2 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg">
                          <ThumbsDown className="h-4 w-4 text-white" />
                        </div>
                        <span className="text-red-600 dark:text-red-400">Points to Consider</span>
                      </div>
                      <ul className="space-y-2">
                        {displayProduct.aiInsights.cons.map((con: string, index: number) => (
                          <li 
                            key={index} 
                            className="flex items-start gap-3 p-3 bg-red-50/50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800 hover:scale-105 transition-all duration-300 animate-fadeIn"
                            style={{ animationDelay: `${index * 0.1}s` }}
                          >
                            <Info className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-700 dark:text-gray-300">{con}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </TabsContent>

                  <TabsContent value="features" className="mt-6 animate-fadeIn">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                          <CheckCircle2 className="h-4 w-4 text-white" />
                        </div>
                        <span className="text-blue-600 dark:text-blue-400">Key Specifications</span>
                      </div>
                      <div className="grid grid-cols-1 gap-3">
                        {displayProduct.features.slice(0, 6).map((feature: any, index: number) => (
                          <div 
                            key={index} 
                            className="flex items-start gap-3 p-3 bg-blue-50/50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800 hover:scale-105 transition-all duration-300 animate-fadeIn"
                            style={{ animationDelay: `${index * 0.1}s` }}
                          >
                            <div className="w-2 h-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mt-2 flex-shrink-0 animate-pulse" />
                            <div className="text-sm flex-1">
                              <span className="text-gray-900 dark:text-white">{feature.name}:</span>{' '}
                              <span className="text-gray-600 dark:text-gray-400">{feature.value}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="ratings" className="mt-6 animate-fadeIn">
                    <div className="space-y-6">
                      {/* Overall Rating */}
                      <div className="flex items-center gap-6 p-6 bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 rounded-xl border border-yellow-200 dark:border-yellow-800">
                        <div className="text-center">
                          <div className="text-5xl bg-gradient-to-r from-yellow-600 to-amber-600 bg-clip-text text-transparent mb-2">
                            {aggregateRating}
                          </div>
                          <div className="flex items-center gap-1 mb-1">
                            {[...Array(5)].map((_, i) => (
                              <Star 
                                key={i} 
                                className={`h-4 w-4 ${
                                  i < Math.floor(parseFloat(aggregateRating))
                                    ? 'fill-yellow-500 text-yellow-500'
                                    : 'text-gray-300 dark:text-gray-600'
                                }`}
                              />
                            ))}
                          </div>
                          <p className="text-xs text-gray-600 dark:text-gray-400">{totalReviews.toLocaleString()} reviews</p>
                        </div>
                        <div className="flex-1 space-y-3">
                          {ratingBreakdown.map((rating) => (
                            <div key={rating.stars} className="flex items-center gap-3">
                              <span className="text-xs text-gray-600 dark:text-gray-400 w-8">{rating.stars}★</span>
                              <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-gradient-to-r from-yellow-500 to-amber-500 rounded-full transition-all duration-1000 ease-out"
                                  style={{ width: `${rating.percentage}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-600 dark:text-gray-400 w-12 text-right">{rating.percentage}%</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Platform Ratings */}
                      <div className="space-y-3">
                        <h4 className="text-sm text-gray-700 dark:text-gray-300 mb-3">Ratings by Platform</h4>
                        {[
                          { name: 'Amazon', data: displayProduct.platforms.amazon, color: 'from-orange-500 to-yellow-500' },
                          { name: 'Flipkart', data: displayProduct.platforms.flipkart, color: 'from-blue-500 to-indigo-500' },
                          { name: 'Myntra', data: displayProduct.platforms.myntra, color: 'from-pink-500 to-rose-500' }
                        ].map((platform, index) => (
                          <div 
                            key={platform.name} 
                            className="flex items-center justify-between p-3 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700 hover:scale-105 transition-all duration-300 animate-fadeIn"
                            style={{ animationDelay: `${index * 0.1}s` }}
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-sm text-gray-900 dark:text-white w-20">{platform.name}</span>
                              <div className="flex items-center gap-1">
                                <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                                <span className="text-sm text-gray-700 dark:text-gray-300">{platform.data.rating}</span>
                              </div>
                            </div>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {platform.data.reviews.toLocaleString()} reviews
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Price Summary Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fadeIn stagger-3">
          <Card className="border-2 border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 hover:shadow-xl hover:shadow-green-500/20 transition-all duration-500 hover:-translate-y-1 overflow-hidden relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/0 to-emerald-500/0 group-hover:from-green-500/10 group-hover:to-emerald-500/10 transition-all duration-500" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm text-green-900 dark:text-green-100">All time Lowest Price</CardTitle>
              <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg animate-bounce-subtle">
                <TrendingUp className="h-4 w-4 text-white rotate-180" />
              </div>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="text-3xl bg-gradient-to-r from-green-700 to-emerald-700 dark:from-green-400 dark:to-emerald-400 bg-clip-text text-transparent">
                ₹{stats.lowestPrice.toLocaleString()}
              </div>
              <p className="text-xs text-green-600 dark:text-green-400 mt-1">on {stats.lowestPlatform}</p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                Save ₹{(stats.highestPrice - stats.lowestPrice).toLocaleString()} ({((stats.highestPrice - stats.lowestPrice) / stats.highestPrice * 100).toFixed(1)}%)
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 border-blue-200 dark:border-blue-800 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 hover:shadow-xl hover:shadow-blue-500/20 transition-all duration-500 hover:-translate-y-1 overflow-hidden relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 to-indigo-500/0 group-hover:from-blue-500/10 group-hover:to-indigo-500/10 transition-all duration-500" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm text-blue-900 dark:text-blue-100">Average Price</CardTitle>
              <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                <Info className="h-4 w-4 text-white" />
              </div>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="text-3xl bg-gradient-to-r from-blue-700 to-indigo-700 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
                ₹{stats.averagePrice.toLocaleString()}
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">across all platforms</p>
            </CardContent>
          </Card>

          <Card className="border-2 border-orange-200 dark:border-orange-800 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/30 dark:to-red-950/30 hover:shadow-xl hover:shadow-orange-500/20 transition-all duration-500 hover:-translate-y-1 overflow-hidden relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500/0 to-red-500/0 group-hover:from-orange-500/10 group-hover:to-red-500/10 transition-all duration-500" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm text-orange-900 dark:text-orange-100">All time Highest Price</CardTitle>
              <div className="p-2 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="text-3xl bg-gradient-to-r from-orange-700 to-red-700 dark:from-orange-400 dark:to-red-400 bg-clip-text text-transparent">
                ₹{stats.highestPrice.toLocaleString()}
              </div>
              <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">on {stats.highestPlatform}</p>
            </CardContent>
          </Card>
        </div>

        {/* Cross-Platform Price Difference Summary */}
        {stats.lowestPrice > 0 && (
          <Card className="border-2 border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50/80 to-emerald-50/80 dark:from-green-950/30 dark:to-emerald-950/30 backdrop-blur-sm hover:shadow-xl hover:shadow-green-500/20 transition-all duration-500 animate-fadeIn">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-green-700 dark:text-green-300">
                <div className="p-2 bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl shadow-lg">
                  <Award className="h-5 w-5 text-white" />
                </div>
                Current Price Comparison Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Best Price */}
                <div className="bg-white/80 dark:bg-gray-800/80 rounded-xl p-4 border border-green-200 dark:border-green-800">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Lowest Price</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    ₹{stats.lowestPrice.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 capitalize">on {stats.lowestPlatform}</p>
                </div>

                {/* Price Difference */}
                <div className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/30 dark:to-red-950/30 rounded-xl p-4 border border-orange-200 dark:border-orange-800">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Price Difference</p>
                  <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                    ₹{(stats.highestPrice - stats.lowestPrice).toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {stats.highestPrice > stats.lowestPrice 
                      ? `${Math.round(((stats.highestPrice - stats.lowestPrice) / stats.highestPrice) * 100)}% cheaper`
                      : 'Same price on all platforms'
                    }
                  </p>
                </div>

                {/* Highest Price */}
                <div className="bg-white/80 dark:bg-gray-800/80 rounded-xl p-4 border border-red-200 dark:border-red-800">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Highest Price</p>
                  <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                    ₹{stats.highestPrice.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 capitalize">on {stats.highestPlatform}</p>
                </div>
              </div>

              {/* Recommendation Banner */}
              {stats.highestPrice > stats.lowestPrice ? (
                <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl p-4 flex items-center gap-3">
                  <div className="p-2 bg-white/20 rounded-lg">
                    <TrendingDown className="h-6 w-6" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold">Best Deal Available!</p>
                    <p className="text-sm text-green-100">
                      Save ₹{(stats.highestPrice - stats.lowestPrice).toLocaleString()} by buying from {stats.lowestPlatform}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl p-4 flex items-center gap-3">
                  <div className="p-2 bg-white/20 rounded-lg">
                    <Info className="h-6 w-6" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold">Same Price Across Platforms</p>
                    <p className="text-sm text-blue-100">
                      This product is currently priced identically on all available platforms at ₹{stats.lowestPrice.toLocaleString()}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Price Comparison Table */}
        <div className="animate-fadeIn stagger-4">
          <PriceTable
            amazon={{ ...displayProduct.platforms.amazon, productName: displayProduct.name }}
            flipkart={{ ...displayProduct.platforms.flipkart, productName: displayProduct.name }}
            myntra={{ ...displayProduct.platforms.myntra, productName: displayProduct.name }}
            meesho={displayProduct.platforms.meesho ? { ...displayProduct.platforms.meesho, productName: displayProduct.name } : undefined}
          />
        </div>

        {/* Price History Graph */}
        <Card className="border-2 border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm hover:shadow-xl transition-all duration-500 animate-fadeIn stagger-5">
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <CardTitle className="flex items-center gap-2">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-white" />
                </div>
                Price Variation Over Time
              </CardTitle>
              <div className="flex gap-2">
                <Button
                  variant={priceView === 'daily' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPriceView('daily')}
                  className={`${priceView === 'daily' ? 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg' : ''} hover:scale-105 transition-all duration-300`}
                >
                  30 Days
                </Button>
                <Button
                  variant={priceView === 'monthly' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPriceView('monthly')}
                  className={`${priceView === 'monthly' ? 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg' : ''} hover:scale-105 transition-all duration-300`}
                >
                  6 Months
                </Button>
                <Button
                  variant={priceView === 'yearly' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPriceView('yearly')}
                  className={`${priceView === 'yearly' ? 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg' : ''} hover:scale-105 transition-all duration-300`}
                >
                  1 Year
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              {(() => {
                const chartData = priceView === 'daily' ? displayProduct.priceHistory.daily :
                  priceView === 'monthly' ? displayProduct.priceHistory.monthly :
                  displayProduct.priceHistory.yearly;
                
                console.log('📊 Price History Chart Data:', chartData);
                console.log('📊 Price View:', priceView);
                
                return (
                  <PriceHistoryChart
                    data={chartData}
                    view={priceView}
                  />
                );
              })()}
            </div>
          </CardContent>
        </Card>

        {/* Review Insights Dashboard */}
        <div className="animate-fadeIn stagger-6">
          <ReviewInsightsDashboard
            productName={(displayProduct as any).title || displayProduct.name || 'Product'}
            overallSentiment={sentimentData?.overall_sentiment || { positive: 0, neutral: 0, negative: 0 }}
            keyTopics={sentimentData?.key_topics || []}
            controversyScore={sentimentData?.controversy_score || 0}
            reliabilityScore={sentimentData?.reliability_score || 0}
            aiConfidence={sentimentData?.ai_confidence || 0}
            loading={sentimentLoading}
          />
        </div>

        {/* Question Answering */}
        <div className="animate-fadeIn stagger-7">
          <QuestionAnswering
            productName={(displayProduct as any).title || displayProduct.name || 'Product'}
            productId={(displayProduct as any)._id || product._id}
          />
        </div>

        {/* Full Product Specifications */}
        <Card className="border-2 border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm hover:shadow-xl transition-all duration-500 animate-fadeIn stagger-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <div className="p-2 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-white" />
              </div>
              Full Product Information & Specifications
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {displayProduct.features.map((feature: any, index: number) => (
                <div 
                  key={index} 
                  className="flex items-start gap-3 p-4 bg-gradient-to-br from-gray-50 to-blue-50/30 dark:from-gray-900 dark:to-blue-950/30 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-lg hover:scale-105 transition-all duration-300 animate-fadeIn group"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <CheckCircle2 className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0 group-hover:scale-110 transition-transform" />
                  <div>
                    <div className="text-sm text-gray-900 dark:text-white">{feature.name}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{feature.value}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
