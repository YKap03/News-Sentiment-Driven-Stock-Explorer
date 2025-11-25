import TickerSelector from './TickerSelector';

interface ControlsSectionProps {
  ticker: string;
  startDate: string;
  endDate: string;
  loading: boolean;
  onTickerChange: (ticker: string) => void;
  onAnalyze: () => void;
}

export default function ControlsSection({
  ticker,
  startDate,
  endDate,
  loading,
  onTickerChange,
  onAnalyze
}: ControlsSectionProps) {
  
  return (
    <div className="glass-card p-8 mb-12 relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-1 h-full bg-blue-600"></div>
      <div className="mb-6 border-b border-slate-100 pb-6">
        <h2 className="text-2xl font-bold text-slate-900">1. Choose a Scenario</h2>
        <p className="text-slate-500 mt-1">Select a stock ticker to analyze. The date range is fixed for this demonstration.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end">
        {/* Ticker - Spans 4 cols */}
        <div className="lg:col-span-4">
          <TickerSelector value={ticker} onChange={onTickerChange} />
        </div>

        {/* Date Range - Spans 6 cols */}
        <div className="lg:col-span-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-70 pointer-events-none select-none">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                readOnly
                className="w-full px-4 py-2.5 border border-slate-200 rounded-lg bg-slate-50 text-slate-500 font-medium focus:ring-0"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                readOnly
                className="w-full px-4 py-2.5 border border-slate-200 rounded-lg bg-slate-50 text-slate-500 font-medium focus:ring-0"
              />
            </div>
          </div>
          <div className="mt-3 flex items-center text-xs font-medium text-amber-600 bg-amber-50 px-3 py-1.5 rounded-md border border-amber-100 inline-block">
            <span>⚠️ Demo Mode: Data limited to {startDate} – {endDate}</span>
          </div>
        </div>

        {/* Analyze Button - Spans 2 cols */}
        <div className="lg:col-span-2">
          <button
            onClick={onAnalyze}
            disabled={loading || !ticker}
            className="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:shadow-lg hover:shadow-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-all transform active:scale-95"
          >
            {loading ? (
                <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                </span>
            ) : 'Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
}
