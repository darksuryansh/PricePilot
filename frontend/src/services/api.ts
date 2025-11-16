// API service for backend integration
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:5000';

export interface ProductData {
  _id: string;
  asin?: string;
  product_id?: string;
  name: string;
  title?: string;
  description: string;
  image: string;
  current_price: number;
  original_price?: number;
  rating?: number;
  reviews_count: number;
  platform: string;
  url: string;
  features: Array<{ [key: string]: string }>;
  specifications: { [key: string]: any };
  scraped_at: string;
  crossPlatformProducts?: ProductData[];
}

export interface PriceHistoryEntry {
  date: string;
  price: number;
  platform: string;
}

export interface PriceStats {
  current_price: number;
  lowest_price: number;
  highest_price: number;
  average_price: number;
  price_drop_percentage: number;
}

export interface Review {
  _id: string;
  rating: string;
  review_text: string;
  reviewer_name?: string;
  review_date?: string;
  verified_purchase?: boolean;
}

export interface AIInsights {
  insights: string;
  pros: string[];
  cons: string[];
  recommendation: string;
  recommendationScore: number;
}

// Scrape product from URL
export async function scrapeProduct(url: string): Promise<{ 
  success: boolean; 
  product_id: string; 
  platform: string; 
  message?: string; 
  error?: string;
  cross_platform_matches?: Array<{ platform: string; product_id: string; title: string; price: string; url: string }>;
}> {
  const response = await fetch(`${API_BASE_URL}/api/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to scrape product');
  }

  return response.json();
}

// Get product details
export async function getProduct(productId: string): Promise<ProductData> {
  const response = await fetch(`${API_BASE_URL}/api/product/${productId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get product');
  }

  return response.json();
}

// Get price history
export async function getPriceHistory(
  productId: string,
  period: 'daily' | 'weekly' | 'monthly' = 'daily',
  days: number = 30
): Promise<{ history: PriceHistoryEntry[]; stats: PriceStats }> {
  const response = await fetch(
    `${API_BASE_URL}/api/product/${productId}/price-history?period=${period}&days=${days}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get price history');
  }

  return response.json();
}

// Get reviews
export async function getReviews(productId: string): Promise<Review[]> {
  const response = await fetch(`${API_BASE_URL}/api/product/${productId}/reviews`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get reviews');
  }

  const data = await response.json();
  return data.reviews || [];
}

// Search products
export async function searchProducts(query: string): Promise<ProductData[]> {
  const response = await fetch(`${API_BASE_URL}/api/products/search?q=${encodeURIComponent(query)}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to search products');
  }

  const data = await response.json();
  return data.products || [];
}

// Get recent products
export async function getRecentProducts(limit: number = 10): Promise<ProductData[]> {
  const response = await fetch(`${API_BASE_URL}/api/products/recent?limit=${limit}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get recent products');
  }

  const data = await response.json();
  return data.products || [];
}

// Get AI insights
export async function getAIInsights(productId: string): Promise<AIInsights> {
  const response = await fetch(`${API_BASE_URL}/api/product/${productId}/ai-insights`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get AI insights');
  }

  return response.json();
}

// Get review insights
export async function getReviewInsights(productId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/product/${productId}/review-insights`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get review insights');
  }

  return response.json();
}

// Get sentiment analysis (using Phi-3 LLM)
export async function getSentimentAnalysis(productId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/product/${productId}/sentiment-analysis`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get sentiment analysis');
  }

  return response.json();
}

// Get suggested questions for product Q&A
export async function getSuggestedQuestions(productId: string): Promise<{ questions: string[] }> {
  const response = await fetch(`${API_BASE_URL}/api/product/${productId}/suggested-questions`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get suggested questions');
  }

  return response.json();
}

// Ask a question about a product
export async function askProductQuestion(productId: string, question: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/product/${productId}/ask-question`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to answer question');
  }

  return response.json();
}

// Health check
export async function healthCheck(): Promise<{ status: string; database: string }> {
  const response = await fetch(`${API_BASE_URL}/api/health`);

  if (!response.ok) {
    throw new Error('Backend is not responding');
  }

  return response.json();
}

// Chatbot query
export async function chatbotQuery(
  query: string,
  productId?: string,
  productName?: string,
  conversationHistory?: Array<{ role: string; content: string }>
): Promise<{ response: string; ai_generated: boolean; timestamp?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/chatbot`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      product_id: productId,
      product_name: productName,
      conversation_history: conversationHistory || []
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get chatbot response');
  }

  return response.json();
}

// ==================== AUTHENTICATION API ====================

export interface AuthResponse {
  success: boolean;
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
    picture?: string;
    auth_provider: 'email' | 'google';
  };
}

export interface UserResponse {
  user: {
    id: string;
    email: string;
    name: string;
    picture?: string;
    auth_provider: 'email' | 'google';
  };
}

export async function register(email: string, password: string, name: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Registration failed');
  }

  return response.json();
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Login failed');
  }

  return response.json();
}

export async function googleAuth(token: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/google`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Google authentication failed');
  }

  return response.json();
}

export async function getCurrentUser(token: string): Promise<UserResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch user');
  }

  return response.json();
}

export async function logout(token: string): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Logout failed');
  }

  return response.json();
}

// ==================== PRICE COMPARISON API ====================

export interface PlatformPrice {
  platform: string;
  product_id: string | null;
  title: string | null;
  image: string | null;
  current_price: number | null;
  original_price: number | null;
  discount: number;
  rating: number | null;
  reviews_count: number | null;
  url: string | null;
  availability: boolean;
}

export interface PriceComparisonResult {
  product_name: string;
  platforms: PlatformPrice[];
  best_price: number | null;
  best_platform: string | null;
  worst_price?: number;
  worst_platform?: string;
  price_difference: number;
  savings_percentage?: number;
}

export async function comparePrices(productName: string): Promise<PriceComparisonResult> {
  const response = await fetch(`${API_BASE_URL}/api/compare-prices`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ product_name: productName }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to compare prices');
  }

  return response.json();
}
