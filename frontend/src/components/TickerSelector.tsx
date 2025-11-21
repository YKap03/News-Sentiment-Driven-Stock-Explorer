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
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Stock Ticker
        </label>
        <div className="px-3 py-2 border border-gray-300 rounded-md bg-gray-100 animate-pulse">
          Loading...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Stock Ticker
        </label>
        <div className="px-3 py-2 border border-red-300 rounded-md bg-red-50 text-red-700">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <label htmlFor="ticker" className="block text-sm font-medium text-gray-700 mb-1">
        Stock Ticker
      </label>
      <select
        id="ticker"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {tickers.map((ticker) => (
          <option key={ticker.symbol} value={ticker.symbol}>
            {ticker.symbol} {ticker.name ? `- ${ticker.name}` : ''}
          </option>
        ))}
      </select>
    </div>
  );
}

