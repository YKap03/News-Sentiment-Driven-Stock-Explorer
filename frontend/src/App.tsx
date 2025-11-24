import { useState } from 'react';
import { format } from 'date-fns';
import TickerSelector from './components/TickerSelector';
import DateRangePicker from './components/DateRangePicker';
import SummaryBar from './components/SummaryBar';
import PriceSentimentChart from './components/PriceSentimentChart';
import CorrelationChart from './components/CorrelationChart';
import ReturnsChart from './components/ReturnsChart';
import SentimentDistributionChart from './components/SentimentDistributionChart';
import NewsFeed from './components/NewsFeed';
import ModelDetails from './components/ModelDetails';
import { getSummary } from './api/client';
import type { SummaryResponse } from './types';

function App() {
  const [ticker, setTicker] = useState('');
  // Default to last 30 days
  const [startDate, setStartDate] = useState(() => {
    const start = new Date();
    start.setDate(start.getDate() - 30);
    return format(start, 'yyyy-MM-dd');
  });
  const [endDate, setEndDate] = useState(() => format(new Date(), 'yyyy-MM-dd'));
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!ticker) {
      setError('Please select a ticker');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getSummary(ticker, startDate, endDate);
      setSummary(data);
    } catch (err) {
      console.error('Error fetching analysis:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch analysis';
      setError(errorMessage);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            News & Sentiment Driven Stock Explorer
          </h1>
          <p className="mt-2 text-gray-600">
            Explore how news sentiment relates to stock price movements
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls Panel */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Analysis Controls</h2>
          <div className="space-y-4">
            <TickerSelector value={ticker} onChange={setTicker} />
            <DateRangePicker
              startDate={startDate}
              endDate={endDate}
              onStartDateChange={setStartDate}
              onEndDateChange={setEndDate}
            />
            <button
              onClick={handleAnalyze}
              disabled={loading || !ticker}
              className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {summary && (
          <>
            <SummaryBar data={summary} />
            
            {/* Main Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <PriceSentimentChart
                priceSeries={summary.price_series}
                sentimentSeries={summary.sentiment_series}
              />
              <CorrelationChart
                priceSeries={summary.price_series}
                sentimentSeries={summary.sentiment_series}
              />
            </div>

            {/* Secondary Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <ReturnsChart priceSeries={summary.price_series} />
              <SentimentDistributionChart articles={summary.articles} />
            </div>

            {/* News Feed */}
            <div className="mb-6">
              <NewsFeed articles={summary.articles} />
            </div>
          </>
        )}

        {/* Model Details */}
        <div className="mt-6">
          <ModelDetails />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Built with FastAPI, React, and Machine Learning
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

