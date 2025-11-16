import { Heart, TrendingDown, Bell, Trash2 } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

interface WatchlistPageProps {
  onProductClick: (productKey: string) => void;
}

export function WatchlistPage({ onProductClick }: WatchlistPageProps) {
  const watchlistItems = [
    {
      key: "iphone 15 pro",
      name: "Apple iPhone 15 Pro (128GB)",
      image: "https://images.unsplash.com/photo-1699265837122-7636e128b4b0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWFydHBob25lJTIwcHJvZHVjdHxlbnwxfHx8fDE3NjIwNjA4Nzd8MA&ixlib=rb-4.1.0&q=80&w=1080",
      currentPrice: 129900,
      targetPrice: 125000,
      lowestPlatform: "Amazon",
      priceDropped: true,
      lastChecked: "2 hours ago"
    },
    {
      key: "macbook air m2",
      name: "MacBook Air M2 (8GB, 256GB)",
      image: "https://images.unsplash.com/photo-1511385348-a52b4a160dc2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsYXB0b3AlMjBjb21wdXRlcnxlbnwxfHx8fDE3NjIwNDkzMDh8MA&ixlib=rb-4.1.0&q=80&w=1080",
      currentPrice: 99900,
      targetPrice: 95000,
      lowestPlatform: "Amazon",
      priceDropped: false,
      lastChecked: "1 hour ago"
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Heart className="h-8 w-8 text-red-500 fill-red-500" />
          <h1 className="text-3xl text-gray-900">My Watchlist</h1>
        </div>
        <p className="text-gray-600">Track your favorite products and get price drop alerts</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Tracked Products</p>
              <p className="text-3xl text-gray-900 mt-1">{watchlistItems.length}</p>
            </div>
            <Heart className="h-10 w-10 text-red-500 fill-red-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Price Alerts</p>
              <p className="text-3xl text-gray-900 mt-1">1</p>
            </div>
            <Bell className="h-10 w-10 text-blue-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Savings</p>
              <p className="text-3xl text-green-600 mt-1">₹24,100</p>
            </div>
            <TrendingDown className="h-10 w-10 text-green-600 opacity-20" />
          </div>
        </div>
      </div>

      {/* Watchlist Items */}
      <div className="space-y-4">
        {watchlistItems.map((item) => (
          <div key={item.key} className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden hover:border-blue-300 hover:shadow-lg transition-all">
            <div className="flex flex-col md:flex-row gap-6 p-6">
              {/* Product Image */}
              <button
                onClick={() => onProductClick(item.key)}
                className="w-full md:w-48 aspect-square bg-gray-100 rounded-lg overflow-hidden flex-shrink-0"
              >
                <ImageWithFallback
                  src={item.image}
                  alt={item.name}
                  className="w-full h-full object-contain p-4 hover:scale-105 transition-transform"
                />
              </button>

              {/* Product Info */}
              <div className="flex-1 space-y-4">
                <div>
                  <button
                    onClick={() => onProductClick(item.key)}
                    className="text-xl text-gray-900 hover:text-blue-600 text-left transition-colors"
                  >
                    {item.name}
                  </button>
                  <p className="text-sm text-gray-500 mt-1">Last checked: {item.lastChecked}</p>
                </div>

                {/* Price Info */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs text-gray-600">Current Lowest Price</Label>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl text-gray-900">₹{item.currentPrice.toLocaleString()}</span>
                      <Badge variant="outline" className="bg-blue-50 text-blue-700">
                        on {item.lowestPlatform}
                      </Badge>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`target-${item.key}`} className="text-xs text-gray-600">
                      Target Price (Alert me when below)
                    </Label>
                    <Input
                      id={`target-${item.key}`}
                      type="number"
                      value={item.targetPrice}
                      className="max-w-xs"
                    />
                  </div>
                </div>

                {/* Alert Status */}
                {item.priceDropped && (
                  <div className="flex items-center gap-2 p-3 bg-green-50 border-2 border-green-200 rounded-lg">
                    <TrendingDown className="h-5 w-5 text-green-600 flex-shrink-0" />
                    <span className="text-sm text-green-700">
                      Price dropped below your target! Now at ₹{item.currentPrice.toLocaleString()}
                    </span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-wrap gap-3">
                  <Button
                    onClick={() => onProductClick(item.key)}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    View Comparison
                  </Button>
                  <Button variant="outline">
                    <Bell className="h-4 w-4 mr-2" />
                    Update Alert
                  </Button>
                  <Button variant="outline" className="text-red-600 hover:text-red-700 hover:bg-red-50">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Remove
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State (hidden when there are items) */}
      {watchlistItems.length === 0 && (
        <div className="text-center py-20">
          <Heart className="h-20 w-20 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl text-gray-900 mb-2">Your watchlist is empty</h3>
          <p className="text-gray-600 mb-6">Start tracking products to get price drop alerts</p>
          <Button onClick={() => {}} className="bg-blue-600 hover:bg-blue-700">
            Browse Products
          </Button>
        </div>
      )}
    </div>
  );
}
