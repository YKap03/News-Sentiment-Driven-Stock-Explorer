import type { SummaryResponse } from '../types';
import { format, parseISO } from 'date-fns';

interface SummaryBarProps {
  data: SummaryResponse;
}

export default function SummaryBar({ data }: SummaryBarProps) {
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.1) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (sentiment < -0.1) return 'bg-rose-100 text-rose-800 border-rose-200';
    return 'bg-slate-100 text-slate-800 border-slate-200';
  };

  const getSentimentLabel = (sentiment: number) => {
    if (sentiment > 0.1) return 'Positive';
    if (sentiment < -0.1) return 'Negative';
    return 'Neutral';
  };

  const baseline = data.model_insights?.baseline_positive_rate || 0.52; 
  const prob = data.model_insights?.mean_positive_prob || 0.5;
  
  const sentimentText = data.avg_sentiment > 0.05 ? "positive" : data.avg_sentiment < -0.05 ? "negative" : "neutral";
  const returnText = prob > baseline ? "higher returns" : "lower returns";
  const didTranslate = (data.avg_sentiment > 0 && prob > baseline) || (data.avg_sentiment < 0 && prob < baseline);
  
  const insightText = `During this period, sentiment was ${sentimentText} and ${didTranslate ? "aligned with" : "did NOT translate into"} ${returnText}. The model estimates a ${(prob * 100).toFixed(1)}% chance of positive 3-day returns vs a ${(baseline * 100).toFixed(1)}% baseline.`;

  return (
    <div className="glass-card p-8 mb-12 bg-gradient-to-br from-emerald-50/50 via-white to-blue-50/50 border-emerald-100/50 shadow-lg">
      <div className="flex flex-col md:flex-row md:items-start justify-between mb-6 border-b border-emerald-100/50 pb-6">
          <div className="max-w-3xl">
            <div className="flex items-center gap-2 mb-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <h2 className="text-sm font-bold text-emerald-700 uppercase tracking-wide">Key Strategic Insight</h2>
            </div>
            <p className="text-2xl font-medium text-slate-900 leading-snug">
                {data.model_insights?.comment || insightText}
            </p>
          </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
        <div className="relative pl-4 border-l-2 border-slate-200">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Ticker Symbol</div>
          <div className="text-2xl font-bold text-slate-900 tracking-tight">{data.ticker}</div>
        </div>
        <div className="relative pl-4 border-l-2 border-slate-200">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Analysis Period</div>
          <div className="text-sm font-medium text-slate-700">
            {format(parseISO(data.start_date), 'MMM d')} - {format(parseISO(data.end_date), 'MMM d, yyyy')}
          </div>
        </div>
        <div className="relative pl-4 border-l-2 border-slate-200">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Total Volume</div>
          <div className="text-2xl font-bold text-slate-900 tracking-tight">{data.n_articles} <span className="text-sm font-normal text-slate-400">articles</span></div>
        </div>
        <div className="relative pl-4 border-l-2 border-slate-200">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Avg Sentiment</div>
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold border ${getSentimentColor(data.avg_sentiment)}`}>
            {getSentimentLabel(data.avg_sentiment)} ({data.avg_sentiment.toFixed(2)})
          </span>
        </div>
      </div>
    </div>
  );
}
