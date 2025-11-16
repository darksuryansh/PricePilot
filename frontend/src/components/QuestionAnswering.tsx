import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { 
  MessageCircle,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  Battery,
  TrendingUp,
  Users,
  CheckCircle2,
  Sparkles,
  Send
} from "lucide-react";
import { useState, useEffect } from "react";
import * as api from "../services/api";
import { toast } from "sonner";

interface QuestionAnsweringProps {
  productName: string;
  productId: string;
}

interface QAResult {
  question: string;
  answer: string;
  confidence: number;
  supportingData: {
    positivePercentage: number;
    totalMentions: number;
    commonThemes: string[];
    warnings?: string[];
  };
  verdict: string;
}

export function QuestionAnswering({ productName, productId }: QuestionAnsweringProps) {
  const [question, setQuestion] = useState("");
  const [currentAnswer, setCurrentAnswer] = useState<QAResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [askedQuestions, setAskedQuestions] = useState<string[]>([]);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([
    "Is this good for gaming?",
    "How is the battery life?",
    "Is it worth the price?",
    "How is the camera quality?",
    "Does it heat up during use?",
    "Is it durable?"
  ]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);

  // Load suggested questions on mount
  useEffect(() => {
    const loadSuggestions = async () => {
      try {
        setLoadingSuggestions(true);
        const response = await api.getSuggestedQuestions(productId);
        if (response.questions && response.questions.length > 0) {
          setSuggestedQuestions(response.questions);
        }
      } catch (error) {
        console.error('Failed to load suggested questions:', error);
        // Keep default questions
      } finally {
        setLoadingSuggestions(false);
      }
    };

    loadSuggestions();
  }, [productId]);

  const handleAsk = async (q?: string) => {
    const questionToAsk = q || question;
    if (!questionToAsk.trim()) return;

    setIsLoading(true);
    setAskedQuestions([...askedQuestions, questionToAsk]);
    
    try {
      const result = await api.askProductQuestion(productId, questionToAsk);
      setCurrentAnswer(result);
      setQuestion("");
    } catch (error) {
      console.error('Failed to get answer:', error);
      toast.error('Failed to get answer. Please try again.');
      setCurrentAnswer({
        question: questionToAsk,
        answer: `Unable to analyze reviews for this question right now. Please try again later.`,
        confidence: 0,
        supportingData: {
          positivePercentage: 0,
          totalMentions: 0,
          commonThemes: [],
          warnings: ["Service temporarily unavailable"]
        },
        verdict: "Try again later"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border-2 border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50/50 via-emerald-50/50 to-white dark:from-green-950/30 dark:via-emerald-950/30 dark:to-gray-800 hover:shadow-xl transition-all duration-500 overflow-hidden relative group">
      {/* Animated background */}
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-full blur-3xl animate-pulse pointer-events-none" style={{ animationDelay: '0.5s' }} />
      
      <CardHeader className="relative z-10">
        <CardTitle className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl animate-float shadow-lg">
            <MessageCircle className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <div className="gradient-text text-2xl">Ask Questions About This Product</div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Get AI-powered answers based on real user reviews
            </p>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="relative z-10 space-y-6">
        {/* Question Input */}
        <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-4 border border-green-200 dark:border-green-800">
          <div className="flex gap-3">
            <Input
              placeholder="Ask anything about this product..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="flex-1 h-12 border-2 border-green-200 dark:border-green-800 focus:border-green-500 dark:focus:border-green-400 rounded-xl"
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
            />
            <Button 
              onClick={() => handleAsk()}
              disabled={isLoading || !question.trim()}
              className="h-12 px-6 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Thinking...
                </div>
              ) : (
                <>
                  <Send className="h-5 w-5 mr-2" />
                  Ask
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Suggested Questions */}
        {!currentAnswer && (
          <div className="space-y-3">
            <h4 className="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-green-600 dark:text-green-400" />
              Suggested Questions:
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {suggestedQuestions.map((q, index) => (
                <button
                  key={index}
                  onClick={() => handleAsk(q)}
                  disabled={isLoading}
                  className="p-3 text-left bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700 hover:border-green-400 dark:hover:border-green-500 hover:shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed animate-fadeIn group"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-center gap-2">
                    <MessageCircle className="h-4 w-4 text-green-600 dark:text-green-400 group-hover:scale-110 transition-transform" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{q}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Answer Display */}
        {currentAnswer && (
          <div className="space-y-4 animate-fadeIn">
            {/* Question Header */}
            <div className="bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-xl p-4 border-2 border-green-300 dark:border-green-700">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg flex-shrink-0">
                  <MessageCircle className="h-5 w-5 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="text-lg text-gray-900 dark:text-white mb-2">{currentAnswer.question}</h4>
                  <Badge className={`${
                    currentAnswer.confidence > 85 ? 'bg-green-600' :
                    currentAnswer.confidence > 70 ? 'bg-yellow-600' :
                    'bg-orange-600'
                  } text-white`}>
                    {currentAnswer.confidence}% AI Confidence
                  </Badge>
                </div>
              </div>
            </div>

            {/* AI Answer */}
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-green-200 dark:border-green-800">
              <div className="flex items-start gap-3 mb-4">
                <div className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex-shrink-0">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed flex-1">
                  {currentAnswer.answer}
                </p>
              </div>
            </div>

            {/* Supporting Data */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Positive Sentiment */}
              <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-4 border border-green-200 dark:border-green-800 hover:scale-105 transition-all duration-300">
                <div className="flex items-center gap-3 mb-3">
                  <ThumbsUp className="h-5 w-5 text-green-600 dark:text-green-400" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Positive Sentiment</span>
                </div>
                <div className="text-3xl bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  {currentAnswer.supportingData.positivePercentage}%
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  of users who mentioned this
                </p>
              </div>

              {/* Total Mentions */}
              <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-4 border border-blue-200 dark:border-blue-800 hover:scale-105 transition-all duration-300">
                <div className="flex items-center gap-3 mb-3">
                  <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Total Mentions</span>
                </div>
                <div className="text-3xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  {currentAnswer.supportingData.totalMentions}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  reviews analyzed
                </p>
              </div>
            </div>

            {/* Common Themes */}
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-4 border border-green-200 dark:border-green-800">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                <h5 className="text-gray-900 dark:text-white">Common Themes from Reviews</h5>
              </div>
              <div className="space-y-2">
                {currentAnswer.supportingData.commonThemes.map((theme, index) => (
                  <div 
                    key={index}
                    className="flex items-center gap-2 p-2 bg-green-50/50 dark:bg-green-900/20 rounded-lg animate-fadeIn"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{theme}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Warnings */}
            {currentAnswer.supportingData.warnings && currentAnswer.supportingData.warnings.length > 0 && (
              <div className="bg-orange-50/50 dark:bg-orange-900/20 rounded-xl p-4 border border-orange-200 dark:border-orange-800">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                  <h5 className="text-gray-900 dark:text-white">Points to Consider</h5>
                </div>
                <div className="space-y-2">
                  {currentAnswer.supportingData.warnings.map((warning, index) => (
                    <div 
                      key={index}
                      className="flex items-center gap-2 p-2 bg-orange-100/50 dark:bg-orange-900/30 rounded-lg animate-fadeIn"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="w-2 h-2 bg-orange-500 rounded-full" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{warning}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Verdict */}
            <div className="bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl p-4 border-2 border-purple-300 dark:border-purple-700">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h5 className="text-sm text-gray-600 dark:text-gray-400 mb-1">AI Verdict</h5>
                  <p className="text-gray-900 dark:text-white">{currentAnswer.verdict}</p>
                </div>
              </div>
            </div>

            {/* Ask Another Question Button */}
            <Button
              onClick={() => setCurrentAnswer(null)}
              variant="outline"
              className="w-full h-12 border-2 border-green-300 dark:border-green-700 hover:bg-green-50 dark:hover:bg-green-900/20 hover:scale-105 transition-all duration-300"
            >
              Ask Another Question
            </Button>
          </div>
        )}

        {/* Previously Asked Questions */}
        {askedQuestions.length > 1 && (
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <h5 className="text-sm text-gray-700 dark:text-gray-300 mb-3">Previously Asked:</h5>
            <div className="flex flex-wrap gap-2">
              {askedQuestions.slice(0, -1).map((q, index) => (
                <Badge 
                  key={index}
                  variant="outline"
                  className="text-xs cursor-pointer hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors"
                  onClick={() => handleAsk(q)}
                >
                  {q}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
