import type { SummaryResponse } from '../types';
import { format } from 'date-fns';

interface SummaryBarProps {
  data: SummaryResponse;
}

export default function SummaryBar({ data }: SummaryBarProps) {
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.1) return 'bg-green-100 text-green-800';
    if (sentiment < -0.1) return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getSentimentLabel = (sentiment: number) => {
    if (sentiment > 0.1) return 'Positive';
    if (sentiment < -0.1) return 'Negative';
    return 'Neutral';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div>
          <div className="text-sm text-gray-500">Ticker</div>
          <div className="text-2xl font-bold text-gray-900">{data.ticker}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Date Range</div>
          <div className="text-sm font-medium text-gray-900">
            {format(new Date(data.start_date), 'MMM d, yyyy')} - {format(new Date(data.end_date), 'MMM d, yyyy')}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Articles</div>
          <div className="text-xl font-semibold text-gray-900">{data.n_articles}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Avg Sentiment</div>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getSentimentColor(data.avg_sentiment)}`}>
            {getSentimentLabel(data.avg_sentiment)} ({data.avg_sentiment.toFixed(2)})
          </span>
        </div>
      </div>
      {data.model_insights && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <strong>ML Insight:</strong> {data.model_insights.comment}
          </div>
        </div>
      )}
    </div>
  );
}

