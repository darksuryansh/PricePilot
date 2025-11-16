import { Search, BarChart3, Wallet, ArrowRight } from "lucide-react";

export function HowItWorks() {
  const steps = [
    {
      icon: Search,
      title: "Paste Link / Search",
      description: "Enter a product name or paste a link from Amazon, Flipkart, or Myntra",
      color: "from-blue-500 to-blue-600",
      bgColor: "bg-blue-100 dark:bg-blue-900/30",
      borderColor: "border-blue-300 dark:border-blue-700",
      shadowColor: "shadow-blue-500/20"
    },
    {
      icon: BarChart3,
      title: "View Comparison",
      description: "See real-time prices, ratings, and AI-powered insights across all platforms",
      color: "from-purple-500 to-purple-600",
      bgColor: "bg-purple-100 dark:bg-purple-900/30",
      borderColor: "border-purple-300 dark:border-purple-700",
      shadowColor: "shadow-purple-500/20"
    },
    {
      icon: Wallet,
      title: "Save Money",
      description: "Buy from the platform with the best price and get price drop alerts",
      color: "from-green-500 to-green-600",
      bgColor: "bg-green-100 dark:bg-green-900/30",
      borderColor: "border-green-300 dark:border-green-700",
      shadowColor: "shadow-green-500/20"
    }
  ];

  return (
    <section className="py-24 px-4 bg-white dark:bg-gray-900 transition-colors duration-300 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/5 dark:bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/5 dark:bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-16 space-y-4 animate-fadeIn">
          <h2 className="text-4xl md:text-5xl bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            How It Works
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-lg">Smart shopping made simple in three easy steps</p>
        </div>

        {/* Steps Grid */}
        <div className="relative grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {/* Card */}
              <div className={`relative group bg-white dark:bg-gray-800 rounded-3xl border-2 ${step.borderColor} p-8 hover:shadow-2xl ${step.shadowColor} transition-all duration-500 hover:-translate-y-4 animate-fadeIn stagger-${index + 1}`}>
                {/* Gradient background on hover */}
                <div className={`absolute inset-0 bg-gradient-to-br ${step.color} opacity-0 group-hover:opacity-5 dark:group-hover:opacity-10 rounded-3xl transition-opacity duration-500`} />
                
                <div className="relative flex flex-col items-center text-center space-y-6">
                  {/* Icon with floating animation */}
                  <div className={`relative w-20 h-20 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-xl group-hover:shadow-2xl ${step.shadowColor} transition-all duration-500 group-hover:scale-110 group-hover:rotate-3`}>
                    <step.icon className="h-10 w-10 text-white" />
                    <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${step.color} blur-xl opacity-50 group-hover:opacity-75 transition-opacity duration-500`} />
                  </div>

                  {/* Step number badge */}
                  <div className={`inline-block px-4 py-1.5 ${step.bgColor} rounded-full text-sm border ${step.borderColor} group-hover:scale-110 transition-transform duration-300`}>
                    <span className={`bg-gradient-to-r ${step.color} bg-clip-text text-transparent`}>
                      Step {index + 1}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="space-y-3">
                    <h3 className="text-xl text-gray-900 dark:text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-blue-600 group-hover:to-purple-600 group-hover:bg-clip-text transition-all duration-300">
                      {step.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                      {step.description}
                    </p>
                  </div>

                  {/* Decorative elements */}
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-ping" />
                  <div className="absolute -bottom-2 -left-2 w-3 h-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-ping" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>

              {/* Arrow connector (desktop only) */}
              {/* {index < steps.length - 1 && (
                <div className="hidden md:flex absolute top-1/2 -right-4 z-10 items-center justify-center w-8 h-8">
                  <div className="relative">
                    <ArrowRight className="h-6 w-6 text-gray-300 dark:text-gray-600 transition-colors duration-300" />
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 blur-lg opacity-0 group-hover:opacity-50 transition-opacity duration-300" />
                  </div>
                </div>
              )} */}
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center animate-fadeIn stagger-4">
          <div className="inline-block px-6 py-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-full border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Join <span className="text-blue-600 dark:text-blue-400">1000+</span> smart shoppers saving money every day
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
