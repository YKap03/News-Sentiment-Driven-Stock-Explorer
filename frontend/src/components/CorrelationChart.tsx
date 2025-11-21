import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import type { PricePoint, SentimentPoint } from '../types';

interface CorrelationChartProps {
  priceSeries: PricePoint[];
  sentimentSeries: SentimentPoint[];
}

export default function CorrelationChart({ priceSeries, sentimentSeries }: CorrelationChartProps) {
  // Combine price and sentiment data by date
  const priceMap = new Map(priceSeries.map(p => [p.date, p.close]));
  const sentimentMap = new Map(sentimentSeries.map(s => [s.date, s.sentiment_avg]));

  const allDates = Array.from(new Set([...priceMap.keys(), ...sentimentMap.keys()])).sort();

  // Normalize dates
  const normalizeDate = (d: string | Date): string => {
    if (typeof d === 'string') return d;
    return d.toISOString().split('T')[0];
  };

  const priceMapNormalized = new Map(
    priceSeries.map(p => [normalizeDate(p.date), p.close])
  );
  const sentimentMapNormalized = new Map(
    sentimentSeries.map(s => [normalizeDate(s.date), s.sentiment_avg])
  );

  const allDatesNormalized = Array.from(
    new Set([...priceMapNormalized.keys(), ...sentimentMapNormalized.keys()])
  ).sort();

  // For correlation, we need dates where BOTH price and sentiment exist
  // If sentiment is sparse, we can use the closest sentiment value for each price date
  const scatterData: Array<{date: string; price: number; sentiment: number; color: string}> = [];
  
  // Get all price dates and find closest sentiment for each
  priceMapNormalized.forEach((price, dateStr) => {
    // Try exact match first
    let sentiment = sentimentMapNormalized.get(dateStr);
    
    // If no exact match, find closest sentiment date
    if (sentiment === undefined && sentimentMapNormalized.size > 0) {
      const sentimentDates = Array.from(sentimentMapNormalized.keys()).sort();
      const priceDate = new Date(dateStr);
      
      // Find closest sentiment date (within 7 days)
      let closestDate: string | null = null;
      let minDiff = Infinity;
      
      for (const sentDate of sentimentDates) {
        const diff = Math.abs(new Date(sentDate).getTime() - priceDate.getTime());
        if (diff < minDiff && diff < 7 * 24 * 60 * 60 * 1000) { // Within 7 days
          minDiff = diff;
          closestDate = sentDate;
        }
      }
      
      if (closestDate) {
        sentiment = sentimentMapNormalized.get(closestDate);
      }
    }
    
    if (price !== undefined && sentiment !== undefined) {
      scatterData.push({
        date: dateStr,
        price,
        sentiment,
        // Color based on sentiment
        color: sentiment > 0.1 ? '#10b981' : sentiment < -0.1 ? '#ef4444' : '#6b7280'
      });
    }
  });

  if (scatterData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Price vs Sentiment Correlation</h3>
        <div className="text-center text-gray-500 py-8">
          <p>No sentiment data available for correlation analysis.</p>
          <p className="text-sm mt-2">Sentiment data points: {sentimentSeries.length}</p>
        </div>
      </div>
    );
  }

  // Calculate correlation coefficient
  const n = scatterData.length;
  const avgPrice = scatterData.reduce((sum, d) => sum + d.price, 0) / n;
  const avgSentiment = scatterData.reduce((sum, d) => sum + d.sentiment, 0) / n;

  const numerator = scatterData.reduce(
    (sum, d) => sum + (d.price - avgPrice) * (d.sentiment - avgSentiment),
    0
  );
  const priceVariance = scatterData.reduce((sum, d) => sum + Math.pow(d.price - avgPrice, 2), 0);
  const sentimentVariance = scatterData.reduce(
    (sum, d) => sum + Math.pow(d.sentiment - avgSentiment, 2),
    0
  );

  const correlation = numerator / Math.sqrt(priceVariance * sentimentVariance) || 0;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-2">Price vs Sentiment Correlation</h3>
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          Correlation Coefficient: <span className="font-semibold">{correlation.toFixed(3)}</span>
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {correlation > 0.3
            ? 'Strong positive correlation'
            : correlation > 0.1
            ? 'Moderate positive correlation'
            : correlation > -0.1
            ? 'Weak correlation'
            : correlation > -0.3
            ? 'Moderate negative correlation'
            : 'Strong negative correlation'}
        </p>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart data={scatterData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="sentiment"
            name="Sentiment"
            label={{ value: 'Sentiment Score', position: 'insideBottom', offset: -5 }}
            domain={['dataMin - 0.1', 'dataMax + 0.1']}
          />
          <YAxis
            type="number"
            dataKey="price"
            name="Price"
            label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
            domain={['dataMin - 10', 'dataMax + 10']}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            formatter={(value: number, name: string) => {
              if (name === 'price') {
                return [`$${value.toFixed(2)}`, 'Price'];
              }
              if (name === 'sentiment') {
                return [value.toFixed(3), 'Sentiment'];
              }
              return [value, name];
            }}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend />
          <Scatter name="Price vs Sentiment" data={scatterData} fill="#3b82f6">
            {scatterData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600">
        <p>Each point represents a day. Color: Green (positive sentiment), Red (negative), Gray (neutral)</p>
      </div>
    </div>
  );
}

