import { TrendingUp, Sparkles, ArrowRight, Loader2 } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { Badge } from "./ui/badge";
import { useState, useEffect } from "react";
import * as api from "../services/api";

interface TrendingComparisonProps {
  onProductClick: (productId: string) => void;
}

export function TrendingComparisons({ onProductClick }: TrendingComparisonProps) {
  const [recentProducts, setRecentProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadRecentProducts = async () => {
      try {
        setLoading(true);
        const data = await api.getRecentProducts(6); // Get 6 most recent products
        setRecentProducts(data);
      } catch (error) {
        console.error('Error loading recent products:', error);
        setRecentProducts([]);
      } finally {
        setLoading(false);
      }
    };

    loadRecentProducts();
  }, []);

  // Transform products for display
  const displayProducts = recentProducts.map(product => {
    // Extract image - handle different possible formats
    let image = 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500';
    
    if (product.image && typeof product.image === 'string' && product.image.trim() !== '') {
      image = product.image;
    } else if (product.image_url && typeof product.image_url === 'string' && product.image_url.trim() !== '') {
      image = product.image_url;
    } else if (product.images && Array.isArray(product.images) && product.images.length > 0) {
      const validImages = product.images.filter((img: string) => img && typeof img === 'string' && img.trim() !== '');
      if (validImages.length > 0) {
        image = validImages[0];
      }
    }

    console.log('Product image mapping:', {
      productId: product.asin || product.product_id,
      name: product.name,
      originalImage: product.image,
      mappedImage: image
    });

    return {
      id: product.asin || product.product_id || product._id,
      name: product.name || product.title || 'Unknown Product',
      image: image,
      lowestPrice: product.current_price || 0,
      savings: product.original_price && product.current_price 
        ? product.original_price - product.current_price 
        : 0,
      category: product.platform ? product.platform.charAt(0).toUpperCase() + product.platform.slice(1) : 'Product',
      platform: product.platform || 'unknown'
    };
  });

  return (
    <section className="py-20 px-4 bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-12 animate-fadeIn">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl shadow-lg animate-pulse-glow">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <h2 className="text-3xl md:text-5xl bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                Recently Searched Products
              </h2>
            </div>
            <p className="text-gray-600 dark:text-gray-400">Recently scraped products from the database</p>
          </div>
          <Sparkles className="h-8 w-8 text-blue-600 dark:text-blue-400 animate-pulse" />
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-gray-600 dark:text-gray-400">Loading recent products...</p>
            </div>
          </div>
        ) : displayProducts.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-gray-600 dark:text-gray-400 text-lg">No products scraped yet.</p>
            <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">Start by searching for a product URL above!</p>
          </div>
        ) : (
          /* Product Grid */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {displayProducts.map((product, index) => (
              <button
                key={product.id}
                onClick={() => onProductClick(product.id)}
                className={`group relative bg-white dark:bg-gray-800 rounded-3xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden text-left transition-all duration-500 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-2xl hover:shadow-blue-500/20 hover:-translate-y-2 animate-fadeIn stagger-${index + 1}`}
              >
              {/* Gradient overlay on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 via-purple-500/0 to-pink-500/0 group-hover:from-blue-500/5 group-hover:via-purple-500/5 group-hover:to-pink-500/5 transition-all duration-500 z-10 pointer-events-none" />
              
              {/* Image container with zoom effect */}
              <div className="relative aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-800 overflow-hidden">
                <ImageWithFallback
                  src={product.image}
                  alt={product.name}
                  className="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-700 ease-out"
                />
                {/* Shimmer effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                
                {/* Badge for platform */}
                <div className="absolute top-4 right-4 px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs rounded-full shadow-lg flex items-center gap-1">
                  <Sparkles className="h-3 w-3" />
                  {product.platform}
                </div>
              </div>

              {/* Content */}
              <div className="p-6 space-y-4 relative z-20">
                <div className="flex items-center gap-2">
                  <Badge 
                    variant="secondary" 
                    className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
                  >
                    {product.category}
                  </Badge>
                  <div className="flex-1" />
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 group-hover:translate-x-2 transition-all duration-300" />
                </div>

                <h3 className="text-lg text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">
                  {product.name}
                </h3>

                <div className="space-y-2">
                  <div className="flex items-baseline gap-2">
                    <span className="text-xs text-gray-500 dark:text-gray-400">From</span>
                    <span className="text-3xl bg-gradient-to-r from-green-600 to-emerald-600 dark:from-green-400 dark:to-emerald-400 bg-clip-text text-transparent group-hover:scale-110 transition-transform duration-300 inline-block origin-left">
                      ₹{product.lowestPrice.toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-green-600 to-emerald-600 animate-shimmer" 
                        style={{
                          width: '60%',
                          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                          backgroundSize: '200% 100%'
                        }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    {product.savings > 0 && (
                      <span className="text-xs text-green-600 dark:text-green-400 px-3 py-1 bg-green-50 dark:bg-green-900/20 rounded-full border border-green-200 dark:border-green-800">
                        Save ₹{product.savings.toLocaleString()}
                      </span>
                    )}
                    <span className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors ml-auto">
                      View details →
                    </span>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
        )}
      </div>
    </section>
  );
}
