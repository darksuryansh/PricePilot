import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { 
  ThumbsUp, 
  ThumbsDown, 
  Minus, 
  TrendingUp, 
  Shield, 
  Brain,
  Sparkles,
  AlertCircle
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";

interface SentimentData {
  positive: number;
  neutral: number;
  negative: number;
}

interface KeyTopic {
  topic: string;
  sentiment: number;
  mentions: number;
}

interface ReviewInsightsDashboardProps {
  productName: string;
  overallSentiment?: SentimentData;
  keyTopics?: KeyTopic[];
  controversyScore?: number;
  reliabilityScore?: number;
  aiConfidence?: number;
  loading?: boolean;
}

export function ReviewInsightsDashboard({ 
  productName,
  overallSentiment = { positive: 75, neutral: 15, negative: 10 },
  keyTopics = [],
  controversyScore = 35,
  reliabilityScore = 82,
  aiConfidence = 90,
  loading = false
}: ReviewInsightsDashboardProps) {
  const sentimentData = [
    { name: "Positive", value: overallSentiment.positive, color: "#10b981" },
    { name: "Neutral", value: overallSentiment.neutral, color: "#ffa200ff" },
    { name: "Negative", value: overallSentiment.negative, color: "#ef4444" }
  ];

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.5) return "from-green-500 to-emerald-500";
    if (sentiment > 0) return "from-yellow-500 to-orange-500";
    return "from-red-500 to-rose-500";
  };

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.5) return <ThumbsUp className="h-4 w-4 text-white" />;
    if (sentiment > 0) return <Minus className="h-4 w-4 text-white" />;
    return <ThumbsDown className="h-4 w-4 text-white" />;
  };

  if (loading) {
    return (
      <Card className="border-2 border-purple-200 dark:border-purple-800">
        <CardContent className="p-12 text-center">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            <p className="text-gray-600 dark:text-gray-400">Analyzing reviews with AI...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Check if there's no data (all zeros)
  const hasData = keyTopics.length > 0 || 
                  overallSentiment.positive > 0 || 
                  overallSentiment.neutral > 0 || 
                  overallSentiment.negative > 0;

  if (!hasData) {
    return (
      <Card className="border-2 border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50/50 via-pink-50/50 to-white dark:from-purple-950/30 dark:via-pink-950/30 dark:to-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div className="flex-1">
              <div className="gradient-text text-2xl">Review Insights Dashboard</div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                AI-powered analysis of {productName} reviews
              </p>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-12 text-center">
          <div className="flex flex-col items-center gap-4">
            <AlertCircle className="h-16 w-16 text-gray-400" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                No Reviews Available Yet
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Sentiment analysis will be available once reviews are scraped for this product.
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500">
                Try scraping this product again or check back later after reviews are collected.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50/50 via-pink-50/50 to-white dark:from-purple-950/30 dark:via-pink-950/30 dark:to-gray-800 hover:shadow-xl transition-all duration-500 overflow-hidden relative group">
      {/* Animated background */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-3xl animate-pulse pointer-events-none" />
      
      <CardHeader className="relative z-10">
        <CardTitle className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl animate-float shadow-lg">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <div className="gradient-text text-2xl">Review Insights Dashboard</div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              AI-powered analysis of {productName} reviews
            </p>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="relative z-10 space-y-6">
        {/* Overall Sentiment & Key Metrics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sentiment Pie Chart */}
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-purple-200 dark:border-purple-800 hover:scale-105 transition-all duration-300">
            <h3 className="text-lg text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              Overall Sentiment Distribution
            </h3>
            <div className="flex items-center gap-6">
              <div className="w-48 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {sentimentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex-1 space-y-3">
                {sentimentData.map((item, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div 
                      className="w-4 h-4 rounded-full animate-pulse" 
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300 flex-1">{item.name}</span>
                    <Badge className="bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-700">
                      {item.value}%
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Key Scores */}
          <div className="space-y-4">
            {/* Controversy Score */}
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-5 border border-orange-200 dark:border-orange-800 hover:scale-105 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                  <span className="text-gray-900 dark:text-white font-semibold">Controversy Score</span>
                </div>
                <div className={`text-3xl font-bold ${
                  controversyScore > 70 ? 'text-green-600' :
                  controversyScore >= 30 ? 'text-orange-600' :
                  'text-red-600'
                }`}>
                  {controversyScore}
                  <span className="text-sm text-gray-500 dark:text-gray-400 ml-1">/100</span>
                </div>
              </div>
              <div className="relative">
                <Progress value={controversyScore} className="h-3" />
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-3">
                {controversyScore > 60 ? "High debate among users" :
                 controversyScore > 30 ? "Some mixed opinions" :
                 "General consensus among users"}
              </p>
            </div>

            {/* Reliability Score */}
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-5 border border-blue-200 dark:border-blue-800 hover:scale-105 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-900 dark:text-white font-semibold">Reliability Score</span>
                </div>
                <div className={`text-3xl font-bold ${
                  reliabilityScore > 70 ? 'text-green-600' :
                  reliabilityScore >= 30 ? 'text-orange-600' :
                  'text-red-600'
                }`}>
                  {reliabilityScore}
                  <span className="text-sm text-gray-500 dark:text-gray-400 ml-1">/100</span>
                </div>
              </div>
              <div className="relative">
                <Progress value={reliabilityScore} className="h-3" />
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-3">
                Based on verified purchases and review authenticity
              </p>
            </div>

            {/* AI Confidence */}
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-5 border border-purple-200 dark:border-purple-800 hover:scale-105 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  <span className="text-gray-900 dark:text-white font-semibold">AI Confidence</span>
                </div>
                <div className={`text-3xl font-bold ${
                  aiConfidence > 70 ? 'text-green-600' :
                  aiConfidence >= 30 ? 'text-orange-600' :
                  'text-red-600'
                }`}>
                  {aiConfidence}
                  <span className="text-sm text-gray-500 dark:text-gray-400 ml-1">/100</span>
                </div>
              </div>
              <div className="relative">
                <Progress value={aiConfidence} className="h-3" />
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-3">
                How confident AI is about this analysis
              </p>
            </div>
          </div>
        </div>

        {/* Key Topics Analysis */}
        <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-purple-200 dark:border-purple-800">
          <h3 className="text-lg text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            Key Topics from Reviews
          </h3>
          {keyTopics.length > 0 ? (
            <div className="space-y-4">
              {keyTopics
                .sort((a: KeyTopic, b: KeyTopic) => b.mentions - a.mentions)
                .map((topic: KeyTopic, index: number) => (
                  <div 
                    key={index}
                    className="flex items-center gap-4 p-4 bg-gradient-to-r from-gray-50 to-purple-50/30 dark:from-gray-900/50 dark:to-purple-950/30 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 hover:scale-105 transition-all duration-300 animate-fadeIn group"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className={`p-2 bg-gradient-to-r ${getSentimentColor(topic.sentiment)} rounded-lg`}>
                      {getSentimentIcon(topic.sentiment)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-900 dark:text-white">{topic.topic}</span>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {topic.mentions} mentions
                          </Badge>
                          <Badge className={`bg-gradient-to-r ${getSentimentColor(topic.sentiment)} text-white`}>
                            {topic.sentiment > 0 ? '+' : ''}{(topic.sentiment * 100).toFixed(0)}%
                          </Badge>
                        </div>
                      </div>
                      <Progress 
                        value={Math.abs(topic.sentiment) * 100} 
                        className="h-2"
                      />
                    </div>
                  </div>
                ))}
            </div>
          ) : (
            <p className="text-gray-600 dark:text-gray-400 text-center py-8">
              No key topics identified yet. More reviews needed.
            </p>
          )}
        </div>

        {/* Visual Bar Chart */}
        {/* <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-purple-200 dark:border-purple-800">
          <h3 className="text-lg text-gray-900 dark:text-white mb-4">Topic Sentiment Visualization</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={keyTopics}>
                <XAxis 
                  dataKey="topic" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  tick={{ fill: 'currentColor', fontSize: 12 }}
                />
                <YAxis tick={{ fill: 'currentColor' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                    border: 'none', 
                    borderRadius: '8px',
                    color: '#fff'
                  }} 
                />
                <Legend />
                <Bar dataKey="mentions" fill="#8b5cf6" name="Mentions" radius={[8, 8, 0, 0]} />
                <Bar 
                  dataKey={(data) => data.sentiment * 100} 
                  fill="#06b6d4" 
                  name="Sentiment Score" 
                  radius={[8, 8, 0, 0]} 
                />
              </BarChart>
            </ResponsiveContainer>
          </div> */}
        {/* </div> */}
      </CardContent>
    </Card>
  );
}
