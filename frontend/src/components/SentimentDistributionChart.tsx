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
import type { SentimentPoint } from '../types';

interface SentimentDistributionChartProps {
  sentimentSeries: SentimentPoint[];
}

export default function SentimentDistributionChart({ sentimentSeries }: SentimentDistributionChartProps) {
  // Handle empty or sparse sentiment data
  if (!sentimentSeries || sentimentSeries.length === 0) {
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

  // Categorize sentiment
  const categories = {
    'Very Negative': 0,
    'Negative': 0,
    'Neutral': 0,
    'Positive': 0,
    'Very Positive': 0
  };

  sentimentSeries.forEach(point => {
    const sentiment = point.sentiment_avg;
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

  const chartData = Object.entries(categories).map(([name, value]) => ({
    name,
    count: value,
    percentage: ((value / sentimentSeries.length) * 100).toFixed(1)
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

