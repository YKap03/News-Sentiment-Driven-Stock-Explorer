import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Bar
} from 'recharts';
import type { PricePoint, SentimentPoint } from '../types';
import { format, parseISO } from 'date-fns';

interface PriceSentimentChartProps {
  priceSeries: PricePoint[];
  sentimentSeries: SentimentPoint[];
}

export default function PriceSentimentChart({ priceSeries, sentimentSeries }: PriceSentimentChartProps) {
  // Combine price and sentiment data by date
  // Handle both string dates and date objects
  const normalizeDate = (d: string | Date): string => {
    if (typeof d === 'string') {
      return d;
    }
    // If it's a Date object, convert to ISO string
    return d.toISOString().split('T')[0];
  };

  const priceMap = new Map(
    priceSeries.map(p => [normalizeDate(p.date), p.close])
  );
  const sentimentMap = new Map(
    sentimentSeries.map(s => [normalizeDate(s.date), s.sentiment_avg])
  );

  const allDates = Array.from(new Set([...priceMap.keys(), ...sentimentMap.keys()])).sort();

  const chartData = allDates.map(dateStr => {
    try {
      return {
        date: dateStr,
        dateFormatted: format(parseISO(dateStr), 'MMM d'),
        price: priceMap.get(dateStr) || null,
        sentiment: sentimentMap.get(dateStr) || 0
      };
    } catch (e) {
      // Fallback if date parsing fails
      return {
        date: dateStr,
        dateFormatted: dateStr,
        price: priceMap.get(dateStr) || null,
        sentiment: sentimentMap.get(dateStr) || 0
      };
    }
  });

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Price & Sentiment Over Time</h3>
        <div className="text-center text-gray-500 py-8">No data available</div>
      </div>
    );
  }

  // Normalize sentiment for visualization (scale to price range)
  const prices = chartData.map(d => d.price).filter(p => p !== null) as number[];
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;

  const normalizedData = chartData.map(d => ({
    ...d,
    sentimentScaled: d.sentiment * (priceRange * 0.3) + minPrice // Scale sentiment to 30% of price range
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-lg font-semibold mb-4">Price & Sentiment Over Time</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={normalizedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="dateFormatted"
            angle={-45}
            textAnchor="end"
            height={80}
            interval="preserveStartEnd"
          />
          <YAxis
            yAxisId="price"
            orientation="left"
            label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
          />
          <YAxis
            yAxisId="sentiment"
            orientation="right"
            label={{ value: 'Sentiment', angle: 90, position: 'insideRight' }}
          />
          <Tooltip
            formatter={(value: number, name: string, props: any) => {
              if (name === 'Price') {
                return [`$${value.toFixed(2)}`, 'Price'];
              }
              if (name === 'Sentiment (scaled)') {
                // Find the original sentiment value for this date
                const dateKey = props.payload?.date;
                const original = chartData.find(d => d.date === dateKey);
                return [original?.sentiment.toFixed(3) || '0.000', 'Sentiment'];
              }
              return [value, name];
            }}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Price"
          />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="sentimentScaled"
            stroke="#10b981"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Sentiment (scaled)"
          />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600">
        <p>Note: Sentiment is scaled for visualization. Hover over data points to see actual values.</p>
      </div>
    </div>
  );
}

