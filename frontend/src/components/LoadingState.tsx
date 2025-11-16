import { Loader2, ShoppingBag } from "lucide-react";

export function LoadingState() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16 relative">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-64 h-64 bg-blue-500/10 dark:bg-blue-500/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-purple-500/10 dark:bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      </div>

      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-3xl border-2 border-gray-200 dark:border-gray-700 p-12 text-center space-y-8 shadow-2xl hover:shadow-blue-500/20 transition-all duration-500 animate-scaleIn relative z-10">
        {/* Main loader icon */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 blur-2xl opacity-50 animate-pulse" />
            <Loader2 className="h-20 w-20 text-blue-600 dark:text-blue-400 animate-spin relative z-10" />
          </div>
        </div>
        
        {/* Text content */}
        <div className="space-y-3 animate-fadeIn stagger-1">
          <h2 className="text-3xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-gradient">
            Comparing Prices...
          </h2>
          <p className="text-gray-600 dark:text-gray-400">Fetching the best deals from Amazon, Flipkart, and Myntra</p>
        </div>

        {/* Platform indicators */}
        <div className="flex items-center justify-center gap-8 flex-wrap">
          <div className="flex items-center gap-3 animate-fadeIn stagger-2">
            <div className="relative">
              <div className="w-4 h-4 bg-orange-500 rounded-full animate-bounce" />
              <div className="absolute inset-0 bg-orange-500 rounded-full blur-md opacity-50 animate-pulse" />
            </div>
            <span className="text-sm text-gray-700 dark:text-gray-300">Amazon</span>
          </div>
          <div className="flex items-center gap-3 animate-fadeIn stagger-3">
            <div className="relative">
              <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
              <div className="absolute inset-0 bg-blue-500 rounded-full blur-md opacity-50 animate-pulse" style={{ animationDelay: '0.15s' }} />
            </div>
            <span className="text-sm text-gray-700 dark:text-gray-300">Flipkart</span>
          </div>
          <div className="flex items-center gap-3 animate-fadeIn stagger-4">
            <div className="relative">
              <div className="w-4 h-4 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
              <div className="absolute inset-0 bg-pink-500 rounded-full blur-md opacity-50 animate-pulse" style={{ animationDelay: '0.3s' }} />
            </div>
            <span className="text-sm text-gray-700 dark:text-gray-300">Myntra</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="pt-6 space-y-3 animate-fadeIn stagger-5">
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-full animate-[loading_2s_ease-in-out_infinite]" style={{ width: '60%' }} />
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
          </div>
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <ShoppingBag className="h-4 w-4 animate-bounce-subtle" />
            <span>Analyzing thousands of products...</span>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-4 right-4 w-16 h-16 border-4 border-blue-200 dark:border-blue-800 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin" style={{ animationDuration: '3s' }} />
        <div className="absolute bottom-4 left-4 w-12 h-12 border-4 border-purple-200 dark:border-purple-800 border-t-purple-600 dark:border-t-purple-400 rounded-full animate-spin" style={{ animationDuration: '2s', animationDirection: 'reverse' }} />
      </div>
    </div>
  );
}
