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
import type { PricePoint } from '../types';
import { format, parseISO } from 'date-fns';

interface ReturnsChartProps {
  priceSeries: PricePoint[];
  syncId?: string;
  onDateClick?: (date: string) => void;
  onDateHover?: (date: string | null) => void;
}

export default function ReturnsChart({ priceSeries, syncId, onDateClick, onDateHover }: ReturnsChartProps) {
  if (priceSeries.length < 2) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6 h-full">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Returns</h3>
        <div className="text-center text-gray-500 py-8">Not enough data available</div>
      </div>
    );
  }

  // Normalize dates and sort
  const normalizeDate = (d: string | Date): string => {
    if (typeof d === 'string') return d;
    return d.toISOString().split('T')[0];
  };

  const sortedPrices = [...priceSeries].sort((a, b) => 
    normalizeDate(a.date).localeCompare(normalizeDate(b.date))
  );

  // Calculate daily returns
  const returnsData = sortedPrices
    .slice(1)
    .map((point, index) => {
      const prevPrice = sortedPrices[index].close;
      const currentPrice = point.close;
      const return_pct = ((currentPrice - prevPrice) / prevPrice) * 100;
      const dateStr = normalizeDate(point.date);

      try {
        return {
          date: dateStr,
          dateFormatted: format(parseISO(dateStr), 'MMM d'),
          return_pct,
          color: return_pct >= 0 ? '#10b981' : '#ef4444'
        };
      } catch (e) {
        return {
          date: dateStr,
          dateFormatted: dateStr,
          return_pct,
          color: return_pct >= 0 ? '#10b981' : '#ef4444'
        };
      }
    });

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 h-full transition-transform hover:-translate-y-0.5 hover:shadow-md">
      <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Daily Returns</h3>
          <p className="text-sm text-gray-500">Green bars are up days, red bars are down days.</p>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart 
            data={returnsData}
            syncId={syncId}
            onClick={(state) => {
                if (state && state.activePayload && state.activePayload.length > 0) {
                    const date = state.activePayload[0].payload.date;
                    if (onDateClick) onDateClick(date);
                }
            }}
            onMouseMove={(state) => {
                if (state.activePayload && state.activePayload.length > 0 && onDateHover) {
                    onDateHover(state.activePayload[0].payload.date);
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
            label={{ value: 'Return (%)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(2)}%`, 'Return']}
            labelFormatter={(label) => `Date: ${label}`}
            cursor={{fill: 'transparent'}}
          />
          <Legend />
          <Bar dataKey="return_pct" name="Daily Return" cursor="pointer">
            {returnsData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600 border-t pt-3">
        <p>Use this to see whether strong sentiment days coincided with large moves.</p>
      </div>
    </div>
  );
}
