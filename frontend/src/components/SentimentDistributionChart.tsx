import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import type { Article } from '../types';

interface SentimentDistributionChartProps {
  articles: Article[];
  onBucketClick?: (bucket: string) => void;
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
            <div className="custom-tooltip">
                <p className="font-bold text-slate-900 mb-1">{label}</p>
                <p className="text-sm text-slate-600">
                    Count: <span className="font-mono font-bold text-slate-900">{data.count}</span>
                </p>
                <p className="text-xs text-slate-400">{data.percentage}% of total</p>
            </div>
        );
    }
    return null;
};

export default function SentimentDistributionChart({ articles, onBucketClick }: SentimentDistributionChartProps) {
  const articlesWithSentiment = articles?.filter(a => a.sentiment_score !== null) || [];
  if (articlesWithSentiment.length === 0) return <div className="glass-card p-8 text-center text-slate-400">No sentiment data</div>;

  const categories = { 'Very Negative': 0, 'Negative': 0, 'Neutral': 0, 'Positive': 0, 'Very Positive': 0 };

  articlesWithSentiment.forEach(article => {
    const s = article.sentiment_score || 0;
    const label = article.sentiment_label?.toLowerCase();
    
    if (label === 'bearish') categories['Very Negative']++;
    else if (label === 'somewhat-bearish') categories['Negative']++;
    else if (label === 'neutral') categories['Neutral']++;
    else if (label === 'somewhat-bullish') categories['Positive']++;
    else if (label === 'bullish') categories['Very Positive']++;
    else if (s < -0.5) categories['Very Negative']++;
    else if (s < -0.1) categories['Negative']++;
    else if (s <= 0.1) categories['Neutral']++;
    else if (s <= 0.5) categories['Positive']++;
    else categories['Very Positive']++;
  });

  const total = articlesWithSentiment.length;
  const chartData = Object.entries(categories).map(([name, value]) => ({
    name, count: value,
    percentage: total > 0 ? ((value / total) * 100).toFixed(1) : '0.0',
    color: name.includes('Positive') ? '#10b981' : name.includes('Negative') ? '#f43f5e' : '#94a3b8'
  }));

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="mb-6">
          <h3 className="text-lg font-bold text-slate-900">Sentiment Balance</h3>
          <p className="text-sm text-slate-500">Is the news flow skewed?</p>
      </div>
      <div className="flex-grow">
        <ResponsiveContainer width="100%" height="100%">
            <BarChart 
                data={chartData}
                onClick={(state) => {
                    if (state && state.activePayload && state.activePayload.length > 0) {
                        const bucket = state.activePayload[0].payload.name;
                        if (onBucketClick) onBucketClick(bucket);
                    }
                }}
            >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis dataKey="name" tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
            <YAxis tick={{fontSize: 12, fill: '#64748b'}} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={{fill: '#f1f5f9'}} />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
            </Bar>
            </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
