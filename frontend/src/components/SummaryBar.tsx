import type { SummaryResponse } from '../types';
import { format, parseISO } from 'date-fns';

interface SummaryBarProps {
  data: SummaryResponse;
}

export default function SummaryBar({ data }: SummaryBarProps) {
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.1) return 'bg-green-100 text-green-800 border-green-200';
    if (sentiment < -0.1) return 'bg-red-100 text-red-800 border-red-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getSentimentLabel = (sentiment: number) => {
    if (sentiment > 0.1) return 'Positive';
    if (sentiment < -0.1) return 'Negative';
    return 'Neutral';
  };

  const baseline = data.model_insights?.baseline_positive_rate || 0.52; // Fallback
  const prob = data.model_insights?.mean_positive_prob || 0.5; // Fallback
  
  // Construct dynamic insight text
  const sentimentText = data.avg_sentiment > 0.05 ? "positive" : data.avg_sentiment < -0.05 ? "negative" : "neutral";
  const returnText = prob > baseline ? "higher returns" : "lower returns";
  const didTranslate = (data.avg_sentiment > 0 && prob > baseline) || (data.avg_sentiment < 0 && prob < baseline);
  
  const insightText = `During this period, sentiment was ${sentimentText} and ${didTranslate ? "aligned with" : "did NOT translate into"} ${returnText}. The model estimates a ${(prob * 100).toFixed(1)}% chance of positive 3-day returns vs a ${(baseline * 100).toFixed(1)}% baseline.`;

  return (
    <div className="bg-emerald-50/50 rounded-xl shadow-sm border border-emerald-100/50 p-6 mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 border-b border-emerald-100 pb-4">
          <div>
            <h2 className="text-sm font-bold text-emerald-800 uppercase tracking-wide">2. Key takeaway</h2>
            <p className="text-xl font-medium text-emerald-900 mt-1">
                {data.model_insights?.comment || insightText}
            </p>
          </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <div className="text-xs text-gray-500 uppercase">Ticker</div>
          <div className="text-lg font-bold text-gray-900">{data.ticker}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500 uppercase">Date Range</div>
          <div className="text-sm font-medium text-gray-900">
            {format(parseISO(data.start_date), 'MMM d')} - {format(parseISO(data.end_date), 'MMM d, yyyy')}
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-500 uppercase">Articles</div>
          <div className="text-lg font-semibold text-gray-900">{data.n_articles}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500 uppercase">Avg Sentiment</div>
          <span className={`inline-block px-3 py-0.5 rounded-full text-sm font-medium border ${getSentimentColor(data.avg_sentiment)}`}>
            {getSentimentLabel(data.avg_sentiment)} ({data.avg_sentiment.toFixed(2)})
          </span>
        </div>
      </div>
    </div>
  );
}
