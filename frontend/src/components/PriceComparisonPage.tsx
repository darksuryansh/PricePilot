import { useState } from 'react';
import { Search, TrendingDown, ShoppingCart, ExternalLink, Star, Award } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import * as api from '../services/api';
import { toast } from 'sonner';

interface PriceComparisonPageProps {
  initialQuery?: string;
  onNavigate: (page: string) => void;
}

export function PriceComparisonPage({ initialQuery = '', onNavigate }: PriceComparisonPageProps) {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [isLoading, setIsLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState<api.PriceComparisonResult | null>(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a product name');
      return;
    }

    setIsLoading(true);
    try {
      const result = await api.comparePrices(searchQuery);
      setComparisonData(result);
      
      const availableCount = result.platforms.filter(p => p.availability).length;
      toast.success(`Found prices on ${availableCount} platforms!`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to compare prices');
      setComparisonData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const getPlatformColor = (platform: string) => {
    const colors: { [key: string]: string } = {
      amazon: 'bg-orange-500',
      flipkart: 'bg-blue-500',
      myntra: 'bg-pink-500',
      meesho: 'bg-purple-500'
    };
    return colors[platform] || 'bg-gray-500';
  };

  const getPlatformName = (platform: string) => {
    return platform.charAt(0).toUpperCase() + platform.slice(1);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8 animate-fadeIn">
          <h1 className="text-4xl font-bold gradient-text mb-3">
            Cross-Platform Price Comparison
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Compare prices across Amazon, Flipkart, Myntra & Meesho instantly
          </p>
        </div>

        {/* Search Bar */}
        <div className="max-w-3xl mx-auto mb-8 animate-fadeIn">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border-2 border-gray-200 dark:border-gray-700">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Enter product name (e.g., iPhone 15, Nike Shoes, HP Laptop)"
                  className="pl-12 h-12 text-lg"
                />
              </div>
              <Button
                onClick={handleSearch}
                disabled={isLoading}
                className="h-12 px-8 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {isLoading ? 'Searching...' : 'Compare Prices'}
              </Button>
            </div>
          </div>
        </div>

        {/* Results */}
        {comparisonData && (
          <div className="space-y-6 animate-fadeIn">
            {/* Summary Card */}
            {comparisonData.best_price && (
              <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl shadow-xl p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Award className="h-6 w-6" />
                      <h2 className="text-2xl font-bold">Best Deal Found!</h2>
                    </div>
                    <p className="text-lg opacity-90">
                      Save ₹{comparisonData.price_difference.toLocaleString()} ({comparisonData.savings_percentage}% off)
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-4xl font-bold">₹{comparisonData.best_price.toLocaleString()}</div>
                    <div className="text-lg opacity-90 capitalize">{comparisonData.best_platform}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Price Comparison Table */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border-2 border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <TrendingDown className="h-5 w-5 text-blue-600" />
                  Price Comparison Table
                </h3>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-900">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">Platform</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">Product</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">Price</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">Discount</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">Rating</th>
                      <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900 dark:text-white">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {comparisonData.platforms.map((platform) => (
                      <tr
                        key={platform.platform}
                        className={`hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors ${
                          platform.platform === comparisonData.best_platform ? 'bg-green-50 dark:bg-green-900/10' : ''
                        }`}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${getPlatformColor(platform.platform)}`} />
                            <span className="font-medium text-gray-900 dark:text-white capitalize">
                              {getPlatformName(platform.platform)}
                            </span>
                            {platform.platform === comparisonData.best_platform && (
                              <Badge className="bg-green-600">Best Price</Badge>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {platform.availability ? (
                            <div className="flex items-center gap-3">
                              {platform.image && (
                                <img
                                  src={platform.image}
                                  alt={platform.title || ''}
                                  className="w-12 h-12 object-cover rounded-lg"
                                />
                              )}
                              <span className="text-sm text-gray-900 dark:text-white line-clamp-2 max-w-xs">
                                {platform.title}
                              </span>
                            </div>
                          ) : (
                            <span className="text-gray-400">Not Available</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {platform.current_price ? (
                            <div>
                              <div className="text-xl font-bold text-gray-900 dark:text-white">
                                ₹{platform.current_price.toLocaleString()}
                              </div>
                              {platform.original_price && platform.original_price > platform.current_price && (
                                <div className="text-sm text-gray-500 line-through">
                                  ₹{platform.original_price.toLocaleString()}
                                </div>
                              )}
                            </div>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {platform.discount > 0 ? (
                            <Badge variant="secondary" className="bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400">
                              {platform.discount}% OFF
                            </Badge>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {platform.rating ? (
                            <div className="flex items-center gap-1">
                              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                              <span className="text-sm font-medium text-gray-900 dark:text-white">{platform.rating}</span>
                              {platform.reviews_count && (
                                <span className="text-xs text-gray-500">({platform.reviews_count})</span>
                              )}
                            </div>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-center">
                          {platform.availability && platform.url ? (
                            <a
                              href={platform.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                            >
                              <ShoppingCart className="h-4 w-4" />
                              Buy Now
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          ) : (
                            <span className="text-gray-400 text-sm">Not Available</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!comparisonData && !isLoading && (
          <div className="text-center py-16 animate-fadeIn">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Search className="h-12 w-12 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Start Comparing Prices
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Enter a product name to see prices across multiple platforms
            </p>
            <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-orange-500" />
                Amazon
              </span>
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-500" />
                Flipkart
              </span>
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-pink-500" />
                Myntra
              </span>
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-purple-500" />
                Meesho
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
