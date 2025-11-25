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
  
  const getReturnForDate = (dateStr: string): string => {
    const priceIdx = priceSeries.findIndex(p => p.date.startsWith(dateStr));
    if (priceIdx === -1 || priceIdx + 3 >= priceSeries.length) return "N/A";
    
    const startPrice = priceSeries[priceIdx].close;
    const endPrice = priceSeries[priceIdx + 3].close;
    const returnPct = ((endPrice - startPrice) / startPrice) * 100;
    
    return `${returnPct > 0 ? '+' : ''}${returnPct.toFixed(1)}%`;
  };

  // Filtering Logic
  let filteredArticles = articles;
  if (selectedDate) {
    filteredArticles = filteredArticles.filter(a => a.date.startsWith(selectedDate));
  }
  if (selectedSentimentBucket) {
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

  // Spotlight Logic
  const articlesWithSentiment = articles.filter(a => a.sentiment_score !== null);
  const mostPositive = [...articlesWithSentiment].sort((a, b) => (b.sentiment_score || 0) - (a.sentiment_score || 0))[0];
  const mostNegative = [...articlesWithSentiment].sort((a, b) => (a.sentiment_score || 0) - (b.sentiment_score || 0))[0];
  
  let maxReturnAbs = -1;
  let maxReturnDate = "";
  for (let i = 1; i < priceSeries.length; i++) {
      const prev = priceSeries[i-1].close;
      const curr = priceSeries[i].close;
      const ret = Math.abs((curr - prev) / prev);
      if (ret > maxReturnAbs) {
          maxReturnAbs = ret;
          maxReturnDate = priceSeries[i].date;
      }
  }
  const largestMoveArticle = articles.find(a => a.date.startsWith(maxReturnDate.split('T')[0]));

  const renderSpotlightCard = (title: string, article?: Article, type?: 'positive' | 'negative' | 'move') => {
      if (!article) return null;
      
      const isPos = (article.sentiment_score || 0) > 0;
      const sentimentColor = isPos ? 'text-emerald-600 bg-emerald-50 border-emerald-100' : 'text-rose-600 bg-rose-50 border-rose-100';
      
      let cardBg = 'bg-white';
      let accentColor = 'bg-slate-200';
      
      if (type === 'positive') { cardBg = 'bg-emerald-50/30 border-emerald-100'; accentColor='bg-emerald-500'; }
      if (type === 'negative') { cardBg = 'bg-rose-50/30 border-rose-100'; accentColor='bg-rose-500'; }
      if (type === 'move') { cardBg = 'bg-blue-50/30 border-blue-100'; accentColor='bg-blue-500'; }

      return (
          <div className={`glass-card p-6 ${cardBg} flex flex-col h-full group relative overflow-hidden`}>
              <div className={`absolute top-0 left-0 w-full h-1 ${accentColor}`}></div>
              <div className="flex justify-between items-start mb-3">
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">{title}</div>
                  <div className={`text-xs font-bold px-2 py-1 rounded-full border ${sentimentColor}`}>
                      {article.sentiment_label || 'Neutral'}
                  </div>
              </div>
              <h4 className="font-bold text-slate-900 mb-3 line-clamp-3 flex-grow leading-snug group-hover:text-blue-600 transition-colors">
                  {article.headline}
              </h4>
              <div className="mt-auto pt-4 border-t border-slate-200/60 flex items-center justify-between text-xs">
                  <div className="text-slate-500">
                      {format(parseISO(article.date), 'MMM d')} • <span className="font-medium text-slate-700">{article.source}</span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] text-slate-400 uppercase">3-Day Impact</span>
                    <span className="font-mono font-bold text-slate-700">{getReturnForDate(article.date.split('T')[0])}</span>
                  </div>
              </div>
          </div>
      );
  };

  return (
    <section>
      <div className="mb-8">
          <h3 className="text-2xl font-bold text-slate-900 mb-2">4. Key News Drivers</h3>
          <p className="text-slate-500">Spotlight on the specific stories that moved the needle.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {renderSpotlightCard("Most Bullish News", mostPositive, 'positive')}
          {renderSpotlightCard("Most Bearish News", mostNegative, 'negative')}
          {largestMoveArticle ? renderSpotlightCard("Largest Price Move", largestMoveArticle, 'move') : null}
      </div>

      <div className="glass-card p-8">
          <div className="flex items-center justify-between mb-6">
              <h4 className="text-lg font-bold text-slate-900">
                  News Feed
              </h4>
              {(selectedDate || selectedSentimentBucket) && (
                  <div className="flex gap-2">
                      {selectedDate && <span className="text-xs font-medium bg-blue-50 text-blue-700 px-2 py-1 rounded-full">Date: {selectedDate}</span>}
                      {selectedSentimentBucket && <span className="text-xs font-medium bg-indigo-50 text-indigo-700 px-2 py-1 rounded-full">Sentiment: {selectedSentimentBucket}</span>}
                  </div>
              )}
          </div>
          <NewsFeed articles={filteredArticles} />
      </div>
    </section>
  );
}
