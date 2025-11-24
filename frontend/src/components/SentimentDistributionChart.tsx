import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import type { Article } from '../types';

interface SentimentDistributionChartProps {
  articles: Article[];
}

export default function SentimentDistributionChart({ articles }: SentimentDistributionChartProps) {
  // Handle empty or sparse sentiment data
  if (!articles || articles.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Sentiment Distribution</h3>
        <div className="text-center text-gray-500 py-8">
          <p>No sentiment data available.</p>
          <p className="text-sm mt-2">This chart requires articles with sentiment scores.</p>
        </div>
      </div>
    );
  }

  // Filter articles that have sentiment scores
  const articlesWithSentiment = articles.filter(a => a.sentiment_score !== null && a.sentiment_score !== undefined);

  if (articlesWithSentiment.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Sentiment Distribution</h3>
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
    
    // Also check sentiment_label for Alpha Vantage labels
    const label = article.sentiment_label;
    if (label) {
      // Map Alpha Vantage labels directly
      if (label === 'Bearish') {
        categories['Very Negative']++;
        return;
      } else if (label === 'Somewhat-Bearish') {
        categories['Negative']++;
        return;
      } else if (label === 'Neutral') {
        categories['Neutral']++;
        return;
      } else if (label === 'Somewhat-Bullish') {
        categories['Positive']++;
        return;
      } else if (label === 'Bullish') {
        categories['Very Positive']++;
        return;
      }
    }
    
    // Fallback to numeric score if label not available
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
    percentage: totalArticles > 0 ? ((value / totalArticles) * 100).toFixed(1) : '0.0'
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Sentiment Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value: number, name: string, props: any) => {
              if (name === 'count') {
                return [
                  `${value} articles (${props.payload.percentage}%)`,
                  'Count'
                ];
              }
              return [value, name];
            }}
          />
          <Legend />
          <Bar dataKey="count" fill="#3b82f6" name="Article Count" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

