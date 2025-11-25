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

export default function PriceSentimentChart({ 
  priceSeries, 
  sentimentSeries, 
  syncId,
  onDateHover,
  onZoomChange
}: PriceSentimentChartProps) {
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
      <div className="bg-white rounded-xl shadow-sm border p-6 h-full">
        <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Price & Sentiment Over Time</h3>
            <p className="text-sm text-gray-500">Did sentiment move with the stock price or diverge?</p>
        </div>
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
  
  // Correlation calculation for annotation
  // Simple Pearson correlation on days where we have both
  let correlation = 0;
  let validPairs = 0;
  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0;

  chartData.forEach(d => {
      if (d.price !== null) {
          const x = d.price;
          const y = d.sentiment;
          sumX += x;
          sumY += y;
          sumXY += x * y;
          sumX2 += x * x;
          sumY2 += y * y;
          validPairs++;
      }
  });

  if (validPairs > 0) {
      const numerator = validPairs * sumXY - sumX * sumY;
      const denominator = Math.sqrt((validPairs * sumX2 - sumX * sumX) * (validPairs * sumY2 - sumY * sumY));
      if (denominator !== 0) correlation = numerator / denominator;
  }

  const absCorr = Math.abs(correlation);
  let annotation = "Price and sentiment showed a strong relationship during this window.";
  if (absCorr < 0.2) {
      annotation = "Price and sentiment moved mostly independently.";
  } else if (absCorr < 0.5) {
      annotation = "Price and sentiment were loosely aligned.";
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 h-full transition-transform hover:-translate-y-0.5 hover:shadow-md">
      <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Price & Sentiment Over Time</h3>
          <p className="text-sm text-gray-500">Did sentiment move with the stock price or diverge?</p>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart 
            data={normalizedData}
            syncId={syncId}
            onMouseMove={(state) => {
                if (state.activeLabel && onDateHover) {
                    // activeLabel is the date string because XAxis dataKey is dateFormatted? 
                    // Wait, XAxis dataKey is "dateFormatted". 
                    // But we want the original date string for sync.
                    // Actually, we should probably use "date" as key for sync if possible, or just use the index.
                    // Let's find the payload.
                     if (state.activePayload && state.activePayload.length > 0) {
                        onDateHover(state.activePayload[0].payload.date);
                    }
                }
            }}
            onMouseLeave={() => onDateHover && onDateHover(null)}
        >
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
          <Brush 
            dataKey="date" 
            height={30} 
            stroke="#8884d8"
            onChange={(range: any) => {
                // Recharts Brush onChange returns { startIndex, endIndex } or similar depending on version
                // Or it might return the actual data if dataKey is set.
                // Check Recharts docs: onChange({ startIndex, endIndex })
                if (onZoomChange && range.startIndex !== undefined && range.endIndex !== undefined) {
                    const start = normalizedData[range.startIndex]?.date;
                    const end = normalizedData[range.endIndex]?.date;
                    if (start && end) {
                        onZoomChange({ start, end });
                    }
                }
            }}
          />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600 border-t pt-3">
        <p>{annotation}</p>
      </div>
    </div>
  );
}
