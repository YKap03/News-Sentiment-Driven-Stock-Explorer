import TickerSelector from './TickerSelector';
import DateRangePicker from './DateRangePicker';
import { subDays, format } from 'date-fns';

interface ControlsSectionProps {
  ticker: string;
  startDate: string;
  endDate: string;
  loading: boolean;
  onTickerChange: (ticker: string) => void;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onAnalyze: () => void;
}

export default function ControlsSection({
  ticker,
  startDate,
  endDate,
  loading,
  onTickerChange,
  onStartDateChange,
  onEndDateChange,
  onAnalyze
}: ControlsSectionProps) {
  
  const setRange = (days: number) => {
    const end = new Date();
    const start = subDays(end, days);
    onEndDateChange(format(end, 'yyyy-MM-dd'));
    onStartDateChange(format(start, 'yyyy-MM-dd'));
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
      <div className="mb-4 border-b pb-4">
        <h2 className="text-xl font-semibold text-gray-900">1. Choose a scenario</h2>
        <p className="text-sm text-gray-500">Pick a stock, a date range, and click Analyze to see how sentiment related to short-term returns.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-end">
        {/* Ticker - Spans 4 cols */}
        <div className="lg:col-span-4">
          <TickerSelector value={ticker} onChange={onTickerChange} />
        </div>

        {/* Date Range - Spans 6 cols */}
        <div className="lg:col-span-6">
          <DateRangePicker 
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={onStartDateChange}
            onEndDateChange={onEndDateChange}
          />
          <div className="flex gap-2 mt-2">
            <button 
                onClick={() => setRange(30)}
                className="text-xs text-blue-600 hover:bg-blue-50 px-2 py-1 rounded border border-transparent hover:border-blue-100 transition-colors"
            >
                Last 30 days
            </button>
            <button 
                onClick={() => setRange(90)}
                className="text-xs text-blue-600 hover:bg-blue-50 px-2 py-1 rounded border border-transparent hover:border-blue-100 transition-colors"
            >
                Last 90 days
            </button>
          </div>
        </div>

        {/* Analyze Button - Spans 2 cols */}
        <div className="lg:col-span-2">
          <button
            onClick={onAnalyze}
            disabled={loading || !ticker}
            className="w-full h-[42px] bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors shadow-sm"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
}

