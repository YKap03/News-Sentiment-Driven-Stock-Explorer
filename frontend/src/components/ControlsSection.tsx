import TickerSelector from './TickerSelector';

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
  // onStartDateChange, // Unused in fixed mode
  // onEndDateChange,   // Unused in fixed mode
  onAnalyze
}: ControlsSectionProps) {
  
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
      <div className="mb-4 border-b pb-4">
        <h2 className="text-xl font-semibold text-gray-900">1. Choose a scenario</h2>
        <p className="text-sm text-gray-500">Pick a stock and click Analyze. Date range is fixed for this demo dataset.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-end">
        {/* Ticker - Spans 4 cols */}
        <div className="lg:col-span-4">
          <TickerSelector value={ticker} onChange={onTickerChange} />
        </div>

        {/* Date Range - Spans 6 cols */}
        <div className="lg:col-span-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 opacity-60 pointer-events-none">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-100 text-gray-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-100 text-gray-500"
              />
            </div>
          </div>
          <div className="mt-2 text-xs text-orange-600 flex items-center">
            <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            Data limited to {startDate} – {endDate}
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
