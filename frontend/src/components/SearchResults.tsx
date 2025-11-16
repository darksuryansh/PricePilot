import { useState } from "react";
import { Filter, SlidersHorizontal, ChevronDown } from "lucide-react";
import { Button } from "./ui/button";
import { Slider } from "./ui/slider";
import { Checkbox } from "./ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { Badge } from "./ui/badge";

interface SearchResultsProps {
  searchQuery: string;
  onProductSelect: (productId: string) => void;
  products: any[];
}

export function SearchResults({ searchQuery, onProductSelect, products = [] }: SearchResultsProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [priceRange, setPriceRange] = useState([0, 200000]);

  // Map products to display format
  const results = products.map(product => ({
    id: product.asin || product.product_id || product._id,
    name: product.title || product.name || 'Unknown Product',
    image: product.image || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
    lowestPrice: product.current_price || product.price || 0,
    platform: product.platform || 'unknown',
    brand: product.brand || (product.title || product.name || '').split(' ')[0] || 'Unknown'
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 relative">
      {/* Animated background */}
      <div className="absolute inset-0 bg-pattern-dots opacity-30 pointer-events-none" />
      
      {/* Header */}
      <div className="mb-6 animate-fadeIn relative z-10">
        <h1 className="text-2xl md:text-3xl text-gray-900 dark:text-white mb-2">
          Search Results for "<span className="gradient-text">{searchQuery}</span>"
        </h1>
        <p className="text-gray-600 dark:text-gray-400">{results.length} products found</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 relative z-10">
        {/* Filters Sidebar */}
        <div className="lg:w-64 flex-shrink-0 animate-fadeIn">
          <div className="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-6 sticky top-20 hover:shadow-lg transition-all duration-300">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg text-gray-900 dark:text-white flex items-center gap-2">
                <Filter className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                Filters
              </h2>
              <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => setShowFilters(!showFilters)}>
                <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </Button>
            </div>

            <div className={`space-y-6 ${showFilters ? 'block' : 'hidden lg:block'}`}>
              {/* Category Filter */}
              <div className="space-y-3">
                <h3 className="text-sm text-gray-700">Category</h3>
                <div className="space-y-2">
                  {['Smartphones', 'Laptops', 'Headphones', 'Watches'].map((cat) => (
                    <label key={cat} className="flex items-center gap-2 cursor-pointer">
                      <Checkbox />
                      <span className="text-sm text-gray-600">{cat}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Brand Filter */}
              <div className="space-y-3">
                <h3 className="text-sm text-gray-700">Brand</h3>
                <div className="space-y-2">
                  {['Apple', 'Samsung', 'Sony', 'Nike'].map((brand) => (
                    <label key={brand} className="flex items-center gap-2 cursor-pointer">
                      <Checkbox />
                      <span className="text-sm text-gray-600">{brand}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Price Range */}
              <div className="space-y-3">
                <h3 className="text-sm text-gray-700">Price Range</h3>
                <Slider
                  value={priceRange}
                  onValueChange={setPriceRange}
                  max={200000}
                  step={1000}
                  className="my-4"
                />
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <span>₹{priceRange[0].toLocaleString()}</span>
                  <span>₹{priceRange[1].toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results Grid */}
        <div className="flex-1">
          {/* Sort and View Options */}
          <div className="flex items-center justify-between mb-6 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-4 animate-fadeIn stagger-1 hover:shadow-lg transition-all duration-300">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Sort by:</span>
            </div>
            <Select defaultValue="relevance">
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="relevance">Relevance</SelectItem>
                <SelectItem value="price-low">Price: Low to High</SelectItem>
                <SelectItem value="price-high">Price: High to Low</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Product Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.length === 0 ? (
              <div className="col-span-full text-center py-12">
                <p className="text-gray-500 dark:text-gray-400">No products found. Try a different search term.</p>
              </div>
            ) : (
              results.map((product, index) => (
                <button
                  key={product.id}
                  onClick={() => onProductSelect(product.id)}
                  className={`group bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-xl hover:shadow-blue-500/20 transition-all duration-500 overflow-hidden text-left hover:-translate-y-2 animate-fadeIn stagger-${index + 2}`}
                >
                  <div className="aspect-square bg-gray-100 overflow-hidden">
                    <ImageWithFallback
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div className="p-4 space-y-3">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs capitalize">{product.platform}</Badge>
                      <Badge variant="outline" className="text-xs">{product.brand}</Badge>
                    </div>
                    <h3 className="text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 transition-colors">
                      {product.name}
                    </h3>
                    <div className="space-y-1">
                      <div className="text-xs text-gray-500">Current price</div>
                      <div className="text-2xl text-green-600">₹{product.lowestPrice.toLocaleString()}</div>
                    </div>
                    <Button className="w-full bg-blue-600 hover:bg-blue-700">
                      View Details
                    </Button>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
