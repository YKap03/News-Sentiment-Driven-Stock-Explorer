import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Brush
} from 'recharts';
import type { PricePoint, SentimentPoint } from '../types';
import { format, parseISO } from 'date-fns';

interface PriceSentimentChartProps {
  priceSeries: PricePoint[];
  sentimentSeries: SentimentPoint[];
  syncId?: string;
  onDateHover?: (date: string | null) => void;
  onZoomChange?: (range: { start: string; end: string } | null) => void;
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="custom-tooltip">
                <p className="font-bold text-slate-900 mb-2">{label}</p>
                {payload.map((entry: any, index: number) => (
                    <div key={index} className="flex items-center gap-2 text-xs mb-1">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                        <span className="text-slate-600 font-medium">{entry.name}:</span>
                        <span className="text-slate-900 font-bold">{entry.value}</span>
                    </div>
                ))}
            </div>
        );
    }
    return null;
};

export default function PriceSentimentChart({ 
  priceSeries, 
  sentimentSeries, 
  syncId,
  onDateHover,
  onZoomChange
}: PriceSentimentChartProps) {
  // ... (Data prep logic remains same) ...
  const normalizeDate = (d: string | Date): string => typeof d === 'string' ? d : d.toISOString().split('T')[0];

  const priceMap = new Map(priceSeries.map(p => [normalizeDate(p.date), p.close]));
  const sentimentMap = new Map(sentimentSeries.map(s => [normalizeDate(s.date), s.sentiment_avg]));
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
      return { date: dateStr, dateFormatted: dateStr, price: null, sentiment: 0 };
    }
  });

  if (chartData.length === 0) return <div className="glass-card p-8 text-center text-slate-400">No data available</div>;

  const prices = chartData.map(d => d.price).filter(p => p !== null) as number[];
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;

  const normalizedData = chartData.map(d => ({
    ...d,
    sentimentScaled: d.sentiment * (priceRange * 0.3) + minPrice
  }));
  
  // Correlation logic
  let correlation = 0;
  let validPairs = 0;
  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0;
  chartData.forEach(d => {
      if (d.price !== null) {
          const x = d.price;
          const y = d.sentiment;
          sumX += x; sumY += y; sumXY += x * y; sumX2 += x * x; sumY2 += y * y;
          validPairs++;
      }
  });
  if (validPairs > 0) {
      const num = validPairs * sumXY - sumX * sumY;
      const den = Math.sqrt((validPairs * sumX2 - sumX * sumX) * (validPairs * sumY2 - sumY * sumY));
      if (den !== 0) correlation = num / den;
  }

  const absCorr = Math.abs(correlation);
  let annotation = "Price and sentiment showed a strong relationship.";
  if (absCorr < 0.2) annotation = "Price and sentiment moved mostly independently.";
  else if (absCorr < 0.5) annotation = "Price and sentiment were loosely aligned.";

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="mb-6">
          <h3 className="text-lg font-bold text-slate-900">Price vs. Sentiment</h3>
          <p className="text-sm text-slate-500">Do news trends precede price moves?</p>
      </div>
      <div className="flex-grow">
        <ResponsiveContainer width="100%" height="100%">
            <ComposedChart 
                data={normalizedData}
                syncId={syncId}
                onMouseMove={(state) => {
                    if (state.activePayload && state.activePayload.length > 0 && onDateHover) {
                        onDateHover(state.activePayload[0].payload.date);
                    }
                }}
                onMouseLeave={() => onDateHover && onDateHover(null)}
            >
            <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis 
                dataKey="dateFormatted" 
                tick={{fontSize: 12, fill: '#64748b'}} 
                axisLine={false}
                tickLine={false}
                minTickGap={30}
            />
            <YAxis 
                yAxisId="price"
                orientation="left"
                tick={{fontSize: 12, fill: '#64748b'}}
                axisLine={false}
                tickLine={false}
                domain={['auto', 'auto']}
                tickFormatter={(val) => `$${val.toFixed(0)}`}
            />
            <YAxis 
                yAxisId="sentiment"
                orientation="right"
                tick={{fontSize: 12, fill: '#64748b'}}
                axisLine={false}
                tickLine={false}
                hide
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{paddingTop: '20px'}} />
            <Line
                yAxisId="price"
                type="monotone"
                dataKey="price"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={false}
                name="Price"
                activeDot={{r: 6, strokeWidth: 0}}
            />
            <Line
                yAxisId="price"
                type="step"
                dataKey="sentimentScaled"
                stroke="#10b981"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
                name="Sentiment Trend"
                connectNulls
            />
            <Brush 
                dataKey="date" 
                height={30} 
                stroke="#cbd5e1"
                fill="#f8fafc"
                tickFormatter={() => ''}
                onChange={(range: any) => {
                    if (onZoomChange && range.startIndex !== undefined) {
                        const start = normalizedData[range.startIndex]?.date;
                        const end = normalizedData[range.endIndex]?.date;
                        if (start && end) onZoomChange({ start, end });
                    }
                }}
            />
            </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 pt-4 border-t border-slate-100 text-xs font-medium text-slate-500 flex items-center gap-2">
        <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
        {annotation}
      </div>
    </div>
  );
}
