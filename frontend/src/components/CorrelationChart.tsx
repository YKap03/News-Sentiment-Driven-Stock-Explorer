import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
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

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
            <div className="custom-tooltip">
                <p className="font-bold text-slate-900 mb-1">{data.date}</p>
                <div className="text-xs space-y-1">
                    <p className="text-slate-600">Sentiment: <span className="font-mono font-bold text-slate-900">{data.sentiment.toFixed(3)}</span></p>
                    <p className="text-slate-600">Price: <span className="font-mono font-bold text-slate-900">${data.price.toFixed(2)}</span></p>
                </div>
            </div>
        );
    }
    return null;
};

export default function CorrelationChart({ priceSeries, sentimentSeries, onDateClick }: CorrelationChartProps) {
  const [selectedPoint, setSelectedPoint] = useState<{date: string; price: number; sentiment: number} | null>(null);
  // ... (Data Prep Logic Same) ...
  const normalizeDate = (d: string | Date): string => typeof d === 'string' ? d : d.toISOString().split('T')[0];
  const priceMapNormalized = new Map(priceSeries.map(p => [normalizeDate(p.date), p.close]));
  const sentimentMapNormalized = new Map(sentimentSeries.map(s => [normalizeDate(s.date), s.sentiment_avg]));
  const scatterData: Array<{date: string; price: number; sentiment: number; color: string}> = [];
  
  priceMapNormalized.forEach((price, dateStr) => {
    let sentiment = sentimentMapNormalized.get(dateStr);
    if (sentiment === undefined && sentimentMapNormalized.size > 0) {
      // Fallback logic (same as before)
      const sentimentDates = Array.from(sentimentMapNormalized.keys()).sort();
      const priceDate = new Date(dateStr);
      let closestDate: string | null = null;
      let minDiff = Infinity;
      for (const sentDate of sentimentDates) {
        const diff = Math.abs(new Date(sentDate).getTime() - priceDate.getTime());
        if (diff < minDiff && diff < 7 * 24 * 60 * 60 * 1000) { minDiff = diff; closestDate = sentDate; }
      }
      if (closestDate) sentiment = sentimentMapNormalized.get(closestDate);
    }
    
    if (price !== undefined && sentiment !== undefined) {
      scatterData.push({
        date: dateStr, price, sentiment,
        color: sentiment > 0.1 ? '#10b981' : sentiment < -0.1 ? '#f43f5e' : '#94a3b8'
      });
    }
  });

  if (scatterData.length === 0) return <div className="glass-card p-8 text-center text-slate-400">No data</div>;

  // Correlation Math
  const n = scatterData.length;
  const avgPrice = scatterData.reduce((sum, d) => sum + d.price, 0) / n;
  const avgSentiment = scatterData.reduce((sum, d) => sum + d.sentiment, 0) / n;
  const numerator = scatterData.reduce((sum, d) => sum + (d.price - avgPrice) * (d.sentiment - avgSentiment), 0);
  const priceVariance = scatterData.reduce((sum, d) => sum + Math.pow(d.price - avgPrice, 2), 0);
  const sentimentVariance = scatterData.reduce((sum, d) => sum + Math.pow(d.sentiment - avgSentiment, 2), 0);
  const correlation = numerator / Math.sqrt(priceVariance * sentimentVariance) || 0;

  return (
    <div className="glass-card p-6 h-full flex flex-col">
        <div className="flex justify-between items-start mb-6">
            <div>
                <h3 className="text-lg font-bold text-slate-900">Sentiment Correlation</h3>
                <p className="text-sm text-slate-500">How closely are they linked?</p>
            </div>
            <div className="text-right bg-blue-50 px-3 py-1 rounded-lg border border-blue-100">
                <div className="text-2xl font-extrabold text-blue-600">{correlation.toFixed(2)}</div>
                <div className="text-[10px] font-bold uppercase text-blue-400">Pearson Coeff</div>
            </div>
        </div>
      
      <div className="flex-grow">
        <ResponsiveContainer width="100%" height="100%">
            <ScatterChart 
                onClick={(state) => {
                    if (state && state.activePayload && state.activePayload.length > 0) {
                        const point = state.activePayload[0].payload;
                        setSelectedPoint(point);
                        if (onDateClick) onDateClick(point.date);
                    }
                }}
            >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis 
                type="number" dataKey="sentiment" name="Sentiment" 
                tick={{fontSize: 12, fill: '#64748b'}}
                axisLine={false} tickLine={false}
                domain={[-1, 1]}
            />
            <YAxis 
                type="number" dataKey="price" name="Price" 
                tick={{fontSize: 12, fill: '#64748b'}}
                axisLine={false} tickLine={false}
                domain={['auto', 'auto']}
                tickFormatter={(val) => `$${val.toFixed(0)}`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
            <Scatter name="Correlation" data={scatterData} cursor="pointer">
                {scatterData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
            </Scatter>
            </ScatterChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 pt-4 border-t border-slate-100 text-xs font-medium text-slate-500">
        {selectedPoint ? (
            <span className="text-blue-600 font-bold">
                Selected: {selectedPoint.date} (Sentiment: {selectedPoint.sentiment.toFixed(2)})
            </span>
        ) : (
            <span>Click a point to filter news for that day.</span>
        )}
      </div>
    </div>
  );
}
