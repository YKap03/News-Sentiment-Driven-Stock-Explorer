import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import type { Article } from '../types';

interface SentimentDistributionChartProps {
  articles: Article[];
  onBucketClick?: (bucket: string) => void;
}

export default function SentimentDistributionChart({ articles, onBucketClick }: SentimentDistributionChartProps) {
  // Handle empty or sparse sentiment data
  if (!articles || articles.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6 h-full">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
        <div className="text-center text-gray-500 py-8">
          <p>No sentiment data available.</p>
        </div>
      </div>
    );
  }

  // Filter articles that have sentiment scores
  const articlesWithSentiment = articles.filter(a => a.sentiment_score !== null && a.sentiment_score !== undefined);

  if (articlesWithSentiment.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6 h-full">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
        <div className="text-center text-gray-500 py-8">
          <p>No articles with sentiment scores available.</p>
        </div>
      </div>
    );
  }

  // Categorize sentiment based on individual article scores
  const categories = {
    'Very Negative': 0,
    'Negative': 0,
    'Neutral': 0,
    'Positive': 0,
    'Very Positive': 0
  };

  articlesWithSentiment.forEach(article => {
    const sentiment = article.sentiment_score;
    if (sentiment === null || sentiment === undefined) {
      return;
    }
    
    const label = article.sentiment_label;
    if (label) {
      const labelLower = label.toLowerCase();
      if (labelLower === 'bearish') {
        categories['Very Negative']++;
        return;
      } else if (labelLower === 'somewhat-bearish') {
        categories['Negative']++;
        return;
      } else if (labelLower === 'neutral') {
        categories['Neutral']++;
        return;
      } else if (labelLower === 'somewhat-bullish') {
        categories['Positive']++;
        return;
      } else if (labelLower === 'bullish') {
        categories['Very Positive']++;
        return;
      }
    }
    
    if (sentiment < -0.5) {
      categories['Very Negative']++;
    } else if (sentiment < -0.1) {
      categories['Negative']++;
    } else if (sentiment <= 0.1) {
      categories['Neutral']++;
    } else if (sentiment <= 0.5) {
      categories['Positive']++;
    } else {
      categories['Very Positive']++;
    }
  });

  const totalArticles = articlesWithSentiment.length;
  const chartData = Object.entries(categories).map(([name, value]) => ({
    name,
    count: value,
    percentage: totalArticles > 0 ? ((value / totalArticles) * 100).toFixed(1) : '0.0',
    color: name.includes('Positive') ? '#10b981' : name.includes('Negative') ? '#ef4444' : '#6b7280'
  }));

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 h-full transition-transform hover:-translate-y-0.5 hover:shadow-md">
        <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Sentiment Distribution</h3>
            <p className="text-sm text-gray-500">How many articles were very negative vs very positive?</p>
        </div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart 
            data={chartData}
            onClick={(state) => {
                if (state && state.activePayload && state.activePayload.length > 0) {
                    const bucket = state.activePayload[0].payload.name;
                    if (onBucketClick) onBucketClick(bucket);
                }
            }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value: number, name: string, props: any) => {
              if (name === 'Article Count') {
                return [
                  `${value} articles (${props.payload.percentage}%)`,
                  'Count'
                ];
              }
              return [value, name];
            }}
            cursor={{fill: 'transparent'}}
          />
          <Legend />
          <Bar dataKey="count" name="Article Count" cursor="pointer">
            {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600 border-t pt-3">
        <p>This shows whether the news flow was skewed positive, negative, or neutral.</p>
      </div>
    </div>
  );
}
