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
import { useState } from 'react';

interface CorrelationChartProps {
  priceSeries: PricePoint[];
  sentimentSeries: SentimentPoint[];
  onDateClick?: (date: string) => void;
}

export default function CorrelationChart({ priceSeries, sentimentSeries, onDateClick }: CorrelationChartProps) {
  const [selectedPoint, setSelectedPoint] = useState<{date: string; price: number; sentiment: number} | null>(null);

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

  // For correlation, we need dates where BOTH price and sentiment exist
  const scatterData: Array<{date: string; price: number; sentiment: number; color: string}> = [];
  
  priceMapNormalized.forEach((price, dateStr) => {
    let sentiment = sentimentMapNormalized.get(dateStr);
    
    // Fallback: find closest sentiment date if missing (within 7 days)
    if (sentiment === undefined && sentimentMapNormalized.size > 0) {
      const sentimentDates = Array.from(sentimentMapNormalized.keys()).sort();
      const priceDate = new Date(dateStr);
      
      let closestDate: string | null = null;
      let minDiff = Infinity;
      
      for (const sentDate of sentimentDates) {
        const diff = Math.abs(new Date(sentDate).getTime() - priceDate.getTime());
        if (diff < minDiff && diff < 7 * 24 * 60 * 60 * 1000) { 
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
        color: sentiment > 0.1 ? '#10b981' : sentiment < -0.1 ? '#ef4444' : '#6b7280'
      });
    }
  });

  if (scatterData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6 h-full">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Price vs Sentiment Correlation</h3>
        <div className="text-center text-gray-500 py-8">No data available</div>
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

  let correlationText = "loosely tracked price moves";
  if (Math.abs(correlation) > 0.5) correlationText = "strongly tracked price moves";
  else if (Math.abs(correlation) < 0.1) correlationText = "had no relation to price moves";

  const correlationLabel = correlation > 0 ? "positive" : "negative";
  const annotation = `Correlation: ${correlation.toFixed(2)} (${correlationLabel}) – sentiment ${correlationText}.`;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 h-full transition-transform hover:-translate-y-0.5 hover:shadow-md">
        <div className="flex justify-between items-start mb-4">
            <div>
                <h3 className="text-lg font-semibold text-gray-900">Price vs Sentiment Correlation</h3>
                <p className="text-sm text-gray-500">Each dot is a day. Higher scores mean more positive news.</p>
            </div>
            <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">{correlation.toFixed(2)}</div>
                <div className="text-xs text-gray-500">Correlation Coeff</div>
            </div>
        </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart 
            data={scatterData} 
            onClick={(state) => {
                if (state && state.activePayload && state.activePayload.length > 0) {
                    const point = state.activePayload[0].payload;
                    setSelectedPoint(point);
                    if (onDateClick) onDateClick(point.date);
                }
            }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="sentiment"
            name="Sentiment"
            label={{ value: 'Sentiment Score', position: 'insideBottom', offset: -5 }}
            domain={[-1, 1]} 
          />
          <YAxis
            type="number"
            dataKey="price"
            name="Price"
            label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
            domain={['auto', 'auto']}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
                if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                        <div className="bg-white p-2 border shadow-sm rounded text-sm">
                            <p className="font-semibold">{data.date}</p>
                            <p>Sentiment: {data.sentiment.toFixed(3)}</p>
                            <p>Price: ${data.price.toFixed(2)}</p>
                        </div>
                    );
                }
                return null;
            }}
          />
          <Scatter name="Price vs Sentiment" data={scatterData} fill="#3b82f6" cursor="pointer">
            {scatterData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      
      <div className="mt-4 text-sm text-gray-600 border-t pt-3">
        <p>{annotation}</p>
        {selectedPoint && (
            <div className="mt-2 p-2 bg-blue-50 rounded text-blue-800 text-xs">
                Selected: <strong>{selectedPoint.date}</strong> | Price: ${selectedPoint.price.toFixed(2)} | Sentiment: {selectedPoint.sentiment.toFixed(2)}
            </div>
        )}
      </div>
    </div>
  );
}
