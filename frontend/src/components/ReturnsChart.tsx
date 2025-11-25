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
import type { PricePoint } from '../types';
import { format, parseISO } from 'date-fns';

interface ReturnsChartProps {
  priceSeries: PricePoint[];
  syncId?: string;
  onDateClick?: (date: string) => void;
  onDateHover?: (date: string | null) => void;
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        const val = payload[0].value;
        const isPos = val >= 0;
        return (
            <div className="custom-tooltip">
                <p className="font-bold text-slate-900 mb-1">{label}</p>
                <p className={`text-sm font-mono font-bold ${isPos ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {isPos ? '+' : ''}{val.toFixed(2)}%
                </p>
            </div>
        );
    }
    return null;
};

export default function ReturnsChart({ priceSeries, syncId, onDateClick, onDateHover }: ReturnsChartProps) {
  if (priceSeries.length < 2) return <div className="glass-card p-8 text-center text-slate-400">No data</div>;

  const normalizeDate = (d: string | Date): string => typeof d === 'string' ? d : d.toISOString().split('T')[0];
  const sortedPrices = [...priceSeries].sort((a, b) => normalizeDate(a.date).localeCompare(normalizeDate(b.date)));

  const returnsData = sortedPrices.slice(1).map((point, index) => {
      const prevPrice = sortedPrices[index].close;
      const currentPrice = point.close;
      const return_pct = ((currentPrice - prevPrice) / prevPrice) * 100;
      const dateStr = normalizeDate(point.date);
      return {
          date: dateStr,
          dateFormatted: format(parseISO(dateStr), 'MMM d'),
          return_pct,
          color: return_pct >= 0 ? '#10b981' : '#f43f5e'
      };
    });

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="mb-6">
          <h3 className="text-lg font-bold text-slate-900">Daily Returns</h3>
          <p className="text-sm text-slate-500">Volatility and momentum check.</p>
      </div>
      <div className="flex-grow">
        <ResponsiveContainer width="100%" height="100%">
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
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis
                dataKey="dateFormatted"
                tick={{fontSize: 12, fill: '#64748b'}}
                axisLine={false} tickLine={false}
                minTickGap={30}
            />
            <YAxis
                tick={{fontSize: 12, fill: '#64748b'}}
                axisLine={false} tickLine={false}
                tickFormatter={(val) => `${val}%`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{fill: '#f1f5f9'}} />
            <Bar dataKey="return_pct" name="Daily Return" radius={[2, 2, 0, 0]}>
                {returnsData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
            </Bar>
            </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
