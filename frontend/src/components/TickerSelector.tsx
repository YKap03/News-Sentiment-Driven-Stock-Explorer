import { useEffect, useState } from 'react';
import { getTickers } from '../api/client';
import type { Ticker } from '../types';

interface TickerSelectorProps {
  value: string;
  onChange: (symbol: string) => void;
}

export default function TickerSelector({ value, onChange }: TickerSelectorProps) {
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTickers() {
      try {
        setLoading(true);
        const data = await getTickers();
        setTickers(data);
        if (data.length > 0 && !value) {
          onChange(data[0].symbol);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tickers');
      } finally {
        setLoading(false);
      }
    }
    loadTickers();
  }, [value, onChange]);

  if (loading) {
    return (
      <div className="w-full">
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
          Stock Ticker
        </label>
        <div className="px-4 py-2.5 border border-slate-200 rounded-lg bg-slate-50 animate-pulse text-slate-400">
          Loading...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full">
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
          Stock Ticker
        </label>
        <div className="px-4 py-2.5 border border-red-300 rounded-lg bg-red-50 text-red-600 text-sm">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <label htmlFor="ticker" className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
        Select Asset
      </label>
      <div className="relative">
        <select
            id="ticker"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full px-4 py-2.5 border border-slate-200 rounded-lg shadow-sm bg-white text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 appearance-none cursor-pointer hover:border-blue-300 transition-colors"
        >
            {tickers.map((ticker) => (
            <option key={ticker.symbol} value={ticker.symbol}>
                {ticker.symbol} — {ticker.name || 'Unknown Company'}
            </option>
            ))}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500">
            <svg className="h-4 w-4 fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
            </svg>
        </div>
      </div>
    </div>
  );
}
