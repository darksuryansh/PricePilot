import { Search, User, Menu, Heart, Moon, Sun, Sparkles, LogOut } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useTheme } from "./ThemeProvider";
import { useAuth } from "../contexts/AuthContext";
import { useState } from "react";
import { LoginModal } from "./auth/LoginModal";
import { RegisterModal } from "./auth/RegisterModal";

interface NavbarProps {
  onNavigate: (page: string) => void;
  onSearch: (query: string) => void;
  isLoggedIn?: boolean;
}

export function Navbar({ onNavigate, onSearch }: NavbarProps) {
  const { theme, toggleTheme } = useTheme();
  const { user, logout, isAuthenticated } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);

  return (
    <nav className="bg-background/80 backdrop-blur-xl border-b border-border sticky top-0 z-50 shadow-sm transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-4">
          {/* Logo with gradient */}
          <button 
            onClick={() => onNavigate('home')}
            className="flex items-center gap-2 flex-shrink-0 group"
          >
            <div className="relative w-10 h-10 bg-gradient-to-br from-blue-600 via-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-blue-500/50 transition-all duration-300 animate-gradient group-hover:scale-110">
              <Sparkles className="w-5 h-5 text-white animate-pulse" />
              <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-400 rounded-xl opacity-0 group-hover:opacity-30 blur-xl transition-opacity duration-300" />
            </div>
            <span className="text-xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-bold">
              PricePilot
            </span>
          </button>

          {/* Desktop Search */}
          <div className="hidden md:flex flex-1 max-w-xl">
            <div className="relative w-full group">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
              <Input
                type="text"
                placeholder="Search for products..."
                className="pl-10 pr-4 bg-background/50 border-border hover:border-primary/50 focus:border-primary transition-all duration-300 backdrop-blur-sm"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.currentTarget.value) {
                    onSearch(e.currentTarget.value);
                  }
                }}
              />
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-3">
            <button 
              onClick={() => onNavigate('home')}
              className="text-sm text-foreground/70 hover:text-primary transition-all duration-300 hover:scale-105 px-3 py-2 rounded-lg hover:bg-primary/5"
            >
              Home
            </button>
            {/* <button 
              onClick={() => onNavigate('compare-prices')}
              className="text-sm text-foreground/70 hover:text-primary transition-all duration-300 hover:scale-105 px-3 py-2 rounded-lg hover:bg-primary/5"
            >
              Compare Prices
            </button> */}
            <button 
              className="text-sm text-foreground/70 hover:text-primary transition-all duration-300 hover:scale-105 px-3 py-2 rounded-lg hover:bg-primary/5"
            >
              Categories
            </button>
            {isAuthenticated ? (
              <>
                <button 
                  onClick={() => onNavigate('watchlist')}
                  className="flex items-center gap-2 text-sm text-foreground/70 hover:text-primary transition-all duration-300 hover:scale-105 px-3 py-2 rounded-lg hover:bg-primary/5"
                >
                  <Heart className="h-4 w-4" />
                  Watchlist
                </button>
                <div className="flex items-center gap-2">
                  {user?.picture && (
                    <img 
                      src={user.picture} 
                      alt={user.name}
                      className="w-8 h-8 rounded-full border-2 border-primary"
                    />
                  )}
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={logout}
                    className="hover:scale-105 transition-transform duration-300"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Button 
                  size="sm"
                  variant="outline"
                  onClick={() => setShowLoginModal(true)}
                  className="hover:scale-105 transition-transform duration-300"
                >
                  <User className="h-4 w-4 mr-2" />
                  Login
                </Button>
                <Button 
                  size="sm" 
                  onClick={() => setShowRegisterModal(true)}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300"
                >
                  Sign Up
                </Button>
              </>
            )}
            
            {/* Dark Mode Toggle */}
            <Button
              variant="outline"
              size="icon"
              onClick={toggleTheme}
              className="relative overflow-hidden hover:scale-110 transition-all duration-300 group"
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 group-hover:opacity-20 transition-opacity" />
            </Button>
          </div>

          {/* Mobile Menu */}
          <div className="flex md:hidden items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={toggleTheme}
              className="hover:scale-110 transition-transform"
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            </Button>
            <Button variant="ghost" size="icon">
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Mobile Search */}
        <div className="md:hidden mt-3">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <Input
              type="text"
              placeholder="Search for products..."
              className="pl-10 pr-4 bg-background/50 border-border hover:border-primary/50 focus:border-primary transition-all duration-300"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.currentTarget.value) {
                  onSearch(e.currentTarget.value);
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Login and Register Modals */}
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onSwitchToRegister={() => {
          setShowLoginModal(false);
          setShowRegisterModal(true);
        }}
      />
      <RegisterModal
        isOpen={showRegisterModal}
        onClose={() => setShowRegisterModal(false)}
        onSwitchToLogin={() => {
          setShowRegisterModal(false);
          setShowLoginModal(true);
        }}
      />
    </nav>
  );
}
