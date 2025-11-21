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
}

export default function ReturnsChart({ priceSeries }: ReturnsChartProps) {
  if (priceSeries.length < 2) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Daily Returns</h3>
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
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Daily Returns (%)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={returnsData}>
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
          />
          <Legend />
          <Bar dataKey="return_pct" name="Daily Return">
            {returnsData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

