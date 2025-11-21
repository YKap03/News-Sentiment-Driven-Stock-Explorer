import type { Article } from '../types';
import { format, parseISO } from 'date-fns';

interface NewsFeedProps {
  articles: Article[];
}

export default function NewsFeed({ articles }: NewsFeedProps) {
  const getSentimentBadge = (label: string | null, score: number | null) => {
    if (!label || score === null) {
      return <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">Unknown</span>;
    }

    const colorClass =
      label === 'Positive' ? 'bg-green-100 text-green-800' :
      label === 'Negative' ? 'bg-red-100 text-red-800' :
      'bg-gray-100 text-gray-800';

    return (
      <span className={`px-2 py-1 text-xs rounded font-semibold ${colorClass}`}>
        {label} ({score.toFixed(2)})
      </span>
    );
  };

  if (articles.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">News Feed</h3>
        <div className="text-center text-gray-500 py-8">No articles found for this period</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">News Feed ({articles.length} articles)</h3>
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {articles.map((article, index) => (
          <div
            key={index}
            className="border-l-4 border-blue-500 pl-4 py-2 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-medium text-gray-900 flex-1">{article.headline}</h4>
              {getSentimentBadge(article.sentiment_label, article.sentiment_score)}
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>{format(parseISO(article.date), 'MMM d, yyyy')}</span>
              <span className="font-medium">{article.source}</span>
              {article.url && (
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  Read more →
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

