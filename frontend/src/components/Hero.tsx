import { Search, Link as LinkIcon, TrendingUp, Zap, Shield } from "lucide-react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./ui/tabs";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { useState } from "react";

interface HeroProps {
  onSearch: (query: string, searchType: 'name' | 'link') => void;
}

export function Hero({ onSearch }: HeroProps) {
  const [searchType, setSearchType] = useState<'name' | 'link'>('name');
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, searchType);
    }
  };

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-blue-950 pt-20 pb-32 px-4 transition-colors duration-300">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/10 dark:bg-blue-500/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-400/10 dark:bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-blue-400/5 to-purple-400/5 dark:from-blue-500/5 dark:to-purple-500/5 rounded-full blur-3xl animate-pulse" />
      </div>

      <div className="max-w-4xl mx-auto text-center space-y-8 relative z-10">
        {/* Feature badges */}
        <div className="flex items-center justify-center gap-4 flex-wrap animate-fadeIn">
          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full border border-blue-200 dark:border-blue-800 shadow-lg hover:scale-105 transition-transform duration-300">
            <Zap className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            <span className="text-xs text-gray-700 dark:text-gray-300">Real-time Prices</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full border border-purple-200 dark:border-purple-800 shadow-lg hover:scale-105 transition-transform duration-300">
            <TrendingUp className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            <span className="text-xs text-gray-700 dark:text-gray-300">AI-Powered</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full border border-green-200 dark:border-green-800 shadow-lg hover:scale-105 transition-transform duration-300">
            <Shield className="h-4 w-4 text-green-600 dark:text-green-400" />
            <span className="text-xs text-gray-700 dark:text-gray-300">Trusted by a lot of users</span>
          </div>
        </div>

        {/* Headline with gradient animation */}
        <div className="space-y-4 animate-fadeIn stagger-1">
          <h1 className="text-4xl md:text-5xl lg:text-7xl text-gray-900 dark:text-white transition-colors duration-300">
            Find the Best Price,{' '}
            <span className="gradient-text animate-gradient inline-block">
              Every Time
            </span>
          </h1>
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Compare prices across <span className="text-blue-600 dark:text-blue-400">Amazon</span>, <span className="text-blue-600 dark:text-blue-400">Flipkart</span>, and <span className="text-pink-600 dark:text-pink-400">Myntra</span> instantly. 
            <br className="hidden md:block" />
            Save money with AI-powered insights.
          </p>
        </div>

        {/* Enhanced Search Bar with glass effect */}
        <div className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 p-8 space-y-6 hover:shadow-blue-500/20 dark:hover:shadow-blue-500/40 transition-all duration-500 animate-fadeIn stagger-2 hover-lift">
          <Tabs value={searchType} onValueChange={(v) => setSearchType(v as 'name' | 'link')} className="w-full">
            <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 bg-gray-100 dark:bg-gray-900 p-1 rounded-2xl">
              <TabsTrigger 
                value="name" 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-blue-700 data-[state=active]:text-white rounded-xl transition-all duration-300 data-[state=active]:shadow-lg data-[state=active]:shadow-blue-500/50"
              >
                <Search className="h-4 w-4 mr-2" />
                Search by Name
              </TabsTrigger>
              <TabsTrigger 
                value="link" 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-blue-700 data-[state=active]:text-white rounded-xl transition-all duration-300 data-[state=active]:shadow-lg data-[state=active]:shadow-blue-500/50"
              >
                <LinkIcon className="h-4 w-4 mr-2" />
                Search by URL
              </TabsTrigger>
            </TabsList>

            <TabsContent value="name" className="animate-fadeIn">
              <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1 group">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl blur opacity-0 group-hover:opacity-20 transition-opacity duration-300" />
                  <Input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for any product (e.g., iPhone 15 Pro, Nike Shoes)"
                    className="relative h-14 px-6 bg-white dark:bg-gray-900 border-2 border-gray-200 dark:border-gray-700 rounded-2xl focus:border-blue-500 dark:focus:border-blue-500 transition-all duration-300 shadow-inner"
                  />
                </div>
                <Button 
                  type="submit" 
                  size="lg" 
                  className="h-14 px-10 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 rounded-2xl shadow-xl shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300 group relative overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    <Search className="h-5 w-5" />
                    Search
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="link" className="animate-fadeIn">
              <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1 group">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl blur opacity-0 group-hover:opacity-20 transition-opacity duration-300" />
                  <Input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Paste link from Amazon, Flipkart, or Myntra"
                    className="relative h-14 px-6 bg-white dark:bg-gray-900 border-2 border-gray-200 dark:border-gray-700 rounded-2xl focus:border-blue-500 dark:focus:border-blue-500 transition-all duration-300 shadow-inner"
                  />
                </div>
                <Button 
                  type="submit" 
                  size="lg" 
                  className="h-14 px-10 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 rounded-2xl shadow-xl shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300 group relative overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Compare
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </Button>
              </form>
            </TabsContent>
          </Tabs>

          {/* Platform badges with hover effects */}
          <div className="flex items-center justify-center gap-3 flex-wrap text-xs">
            <span className="text-gray-500 dark:text-gray-400">Supported platforms:</span>
            <span className="px-4 py-2 bg-gradient-to-r from-orange-100 to-orange-200 dark:from-orange-900/30 dark:to-orange-800/30 text-orange-700 dark:text-orange-300 rounded-full hover:scale-110 hover:shadow-lg transition-all duration-300 cursor-default border border-orange-300 dark:border-orange-700">
              Amazon
            </span>
            <span className="px-4 py-2 bg-gradient-to-r from-blue-100 to-blue-200 dark:from-blue-900/30 dark:to-blue-800/30 text-blue-700 dark:text-blue-300 rounded-full hover:scale-110 hover:shadow-lg transition-all duration-300 cursor-default border border-blue-300 dark:border-blue-700">
              Flipkart
            </span>
            <span className="px-4 py-2 bg-gradient-to-r from-pink-100 to-pink-200 dark:from-pink-900/30 dark:to-pink-800/30 text-pink-700 dark:text-pink-300 rounded-full hover:scale-110 hover:shadow-lg transition-all duration-300 cursor-default border border-pink-300 dark:border-pink-700">
              Myntra
            </span>
          </div>
        </div>

        {/* Trust indicators */}
        <div className="flex items-center justify-center gap-8 text-sm text-gray-600 dark:text-gray-400 animate-fadeIn stagger-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>Live Prices</span>
          </div>
          <div className="hidden sm:flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.5s' }} />
            <span>10,000+ Products</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '1s' }} />
            <span>Trusted Platform</span>
          </div>
        </div>
      </div>
    </section>
  );
}
