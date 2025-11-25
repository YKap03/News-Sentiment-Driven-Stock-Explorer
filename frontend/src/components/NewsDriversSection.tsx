import type { Article, PricePoint } from '../types';
import NewsFeed from './NewsFeed';
import { format, parseISO } from 'date-fns';

interface NewsDriversSectionProps {
  articles: Article[];
  priceSeries: PricePoint[];
  selectedDate: string | null;
  selectedSentimentBucket: string | null;
}

export default function NewsDriversSection({ 
  articles, 
  priceSeries,
  selectedDate,
  selectedSentimentBucket
}: NewsDriversSectionProps) {
  
  // Helper to calculate returns
  const getReturnForDate = (dateStr: string): string => {
    // Find price for this date
    const priceIdx = priceSeries.findIndex(p => p.date.startsWith(dateStr));
    if (priceIdx === -1 || priceIdx + 3 >= priceSeries.length) return "Data not available";
    
    const startPrice = priceSeries[priceIdx].close;
    const endPrice = priceSeries[priceIdx + 3].close;
    const returnPct = ((endPrice - startPrice) / startPrice) * 100;
    
    return `${returnPct > 0 ? '+' : ''}${returnPct.toFixed(1)}%`;
  };

  // 1. Filter articles if needed based on selections
  let filteredArticles = articles;
  if (selectedDate) {
    filteredArticles = filteredArticles.filter(a => a.date.startsWith(selectedDate));
  }
  if (selectedSentimentBucket) {
      // Simple mapping for demo purposes, ideally matches chart logic exactly
      filteredArticles = filteredArticles.filter(a => {
          const s = a.sentiment_score || 0;
          const label = a.sentiment_label?.toLowerCase();
          if (selectedSentimentBucket === 'Very Negative') return s < -0.5 || label === 'bearish';
          if (selectedSentimentBucket === 'Negative') return (s >= -0.5 && s < -0.1) || label === 'somewhat-bearish';
          if (selectedSentimentBucket === 'Neutral') return (s >= -0.1 && s <= 0.1) || label === 'neutral';
          if (selectedSentimentBucket === 'Positive') return (s > 0.1 && s <= 0.5) || label === 'somewhat-bullish';
          if (selectedSentimentBucket === 'Very Positive') return s > 0.5 || label === 'bullish';
          return true;
      });
  }

  // 2. Find spotlight articles (from the FULL list, not filtered, unless we want spotlight to respect filter? 
  // Usually spotlight is global for the period, but let's stick to the provided articles)
  // We'll use the full 'articles' prop for spotlight finding to show global highlights for the period.
  
  const articlesWithSentiment = articles.filter(a => a.sentiment_score !== null);
  
  const mostPositive = [...articlesWithSentiment].sort((a, b) => (b.sentiment_score || 0) - (a.sentiment_score || 0))[0];
  const mostNegative = [...articlesWithSentiment].sort((a, b) => (a.sentiment_score || 0) - (b.sentiment_score || 0))[0];
  
  // Find largest move
  // We need to map articles to dates, and check returns for those dates.
  // Or simply find the date with largest return and pick an article from that date?
  // "article whose date is closest to the day with largest absolute return"
  
  // Calculate daily returns
  let maxReturnAbs = -1;
  let maxReturnDate = "";
  
  for (let i = 1; i < priceSeries.length; i++) {
      const prev = priceSeries[i-1].close;
      const curr = priceSeries[i].close;
      const ret = Math.abs((curr - prev) / prev);
      if (ret > maxReturnAbs) {
          maxReturnAbs = ret;
          maxReturnDate = priceSeries[i].date; // formatting?
      }
  }
  
  // Find article on that date
  const largestMoveArticle = articles.find(a => a.date.startsWith(maxReturnDate.split('T')[0]));

  const renderSpotlightCard = (title: string, article?: Article, type?: 'positive' | 'negative' | 'move') => {
      if (!article) return null;
      
      const sentimentColor = (article.sentiment_score || 0) > 0 ? 'text-green-600' : (article.sentiment_score || 0) < 0 ? 'text-red-600' : 'text-gray-600';
      const borderColor = type === 'positive' ? 'border-green-200 bg-green-50' : type === 'negative' ? 'border-red-200 bg-red-50' : 'border-blue-200 bg-blue-50';
      
      return (
          <div className={`flex-1 p-4 rounded-lg border ${borderColor} shadow-sm transition-all hover:shadow-md`}>
              <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">{title}</div>
              <div className="font-medium text-gray-900 mb-2 line-clamp-2 h-12">{article.headline}</div>
              <div className="flex justify-between items-end mt-2">
                  <div className="text-xs text-gray-500">
                      {format(parseISO(article.date), 'MMM d')} • {article.source}
                  </div>
                  <div className={`text-xs font-bold ${sentimentColor}`}>
                      {article.sentiment_label}
                  </div>
              </div>
              <div className="mt-3 pt-2 border-t border-black/5 flex justify-between items-center">
                  <span className="text-xs text-gray-500">Next 3-day return</span>
                  <span className="text-sm font-mono font-semibold text-gray-700">{getReturnForDate(article.date.split('T')[0])}</span>
              </div>
          </div>
      );
  };

  return (
    <section>
      <div className="mb-6">
          <h3 className="text-xl font-semibold text-gray-900">4. Key news drivers</h3>
          <p className="text-sm text-gray-500">See the most bullish and bearish headlines and how the stock moved around them.</p>
      </div>

      {/* Spotlight Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {renderSpotlightCard("Most Bullish News", mostPositive, 'positive')}
          {renderSpotlightCard("Most Bearish News", mostNegative, 'negative')}
          {largestMoveArticle ? renderSpotlightCard("Largest Price Move", largestMoveArticle, 'move') : (
              <div className="flex-1 p-4 rounded-lg border border-gray-200 bg-gray-50 flex items-center justify-center text-gray-400 text-sm">
                  No articles found on largest move day
              </div>
          )}
      </div>

      {/* Full Feed */}
      <div className="mt-8">
          <h4 className="text-lg font-medium text-gray-900 mb-4">
              All Articles 
              {selectedDate && <span className="ml-2 text-sm font-normal text-gray-500">(Filtered by date: {selectedDate})</span>}
              {selectedSentimentBucket && <span className="ml-2 text-sm font-normal text-gray-500">(Filtered by: {selectedSentimentBucket})</span>}
          </h4>
          <NewsFeed articles={filteredArticles} />
      </div>
    </section>
  );
}
