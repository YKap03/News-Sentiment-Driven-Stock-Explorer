import { useState, useMemo, useRef } from 'react';
import ControlsSection from './components/ControlsSection';
import SummaryBar from './components/SummaryBar';
import PriceSentimentChart from './components/PriceSentimentChart';
import CorrelationChart from './components/CorrelationChart';
import ReturnsChart from './components/ReturnsChart';
import SentimentDistributionChart from './components/SentimentDistributionChart';
import NewsDriversSection from './components/NewsDriversSection';
import ModelReliabilitySection from './components/ModelDetails'; // Refactored component
import { getSummary } from './api/client';
import type { SummaryResponse } from './types';
import { format } from 'date-fns';

function App() {
  // Default date range - Fixed for demo data
  const [ticker, setTicker] = useState('');
  const [startDate, setStartDate] = useState('2025-10-21'); 
  const [endDate, setEndDate] = useState('2025-11-20');
  
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Interactive State
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedSentimentBucket, setSelectedSentimentBucket] = useState<string | null>(null);
  const [zoomRange, setZoomRange] = useState<{ start: string; end: string } | null>(null);
  const [hoveredDate, setHoveredDate] = useState<string | null>(null);

  const newsSectionRef = useRef<HTMLDivElement>(null);

  const handleAnalyze = async () => {
    if (!ticker) {
      setError('Please select a ticker');
      return;
    }

    setLoading(true);
    setError(null);
    // Reset interactive state on new analysis
    setSelectedDate(null);
    setSelectedSentimentBucket(null);
    setZoomRange(null);
    setHoveredDate(null);

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

  // Filter data based on zoomRange
  const filteredSummary = useMemo(() => {
    if (!summary) return null;
    if (!zoomRange) return summary;

    const start = new Date(zoomRange.start).getTime();
    const end = new Date(zoomRange.end).getTime();

    // Helper to check if date is in range
    const isInRange = (dateStr: string) => {
      const d = new Date(dateStr).getTime();
      return d >= start && d <= end;
    };

    return {
      ...summary,
      price_series: summary.price_series.filter(p => isInRange(p.date)),
      sentiment_series: summary.sentiment_series.filter(s => isInRange(s.date)),
      articles: summary.articles.filter(a => isInRange(a.date)),
    };
  }, [summary, zoomRange]);

  // Sync ID for Recharts
  const SYNC_ID = "analysis-sync";

  const handleDateClick = (date: string) => {
      setSelectedDate(date);
      // Scroll to news section if needed
      if (newsSectionRef.current) {
          newsSectionRef.current.scrollIntoView({ behavior: 'smooth' });
      }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* 1.1 Hero Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between">
            <div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                    News & Sentiment Driven Stock Explorer
                </h1>
                <p className="text-sm text-slate-500 mt-1">
                    Explore how ticker-specific news sentiment lined up with short-term stock returns.
                </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* 1.2 Controls Section */}
        <ControlsSection 
            ticker={ticker}
            startDate={startDate}
            endDate={endDate}
            loading={loading}
            onTickerChange={setTicker}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
            onAnalyze={handleAnalyze}
        />

        {error && (
            <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
                {error}
            </div>
        )}

        {filteredSummary && (
            <>
                {/* 1.3 Insight Bar */}
                <SummaryBar data={filteredSummary} />

                {/* 2. Evidence Section */}
                <section className="mb-12">
                    <div className="mb-6 border-b border-gray-200 pb-2">
                        <h2 className="text-2xl font-bold text-gray-900">3. Evidence</h2>
                        <p className="text-gray-500">See how price, sentiment, and returns behaved over this period.</p>
                    </div>

                    <div className="grid gap-6 lg:grid-cols-2">
                        {/* Price & Sentiment */}
                        <div className="lg:h-[450px]">
                            <PriceSentimentChart
                                priceSeries={filteredSummary.price_series}
                                sentimentSeries={filteredSummary.sentiment_series}
                                syncId={SYNC_ID}
                                onDateHover={setHoveredDate}
                                onZoomChange={setZoomRange}
                            />
                        </div>
                        
                        {/* Correlation */}
                        <div className="lg:h-[450px]">
                            <CorrelationChart
                                priceSeries={filteredSummary.price_series}
                                sentimentSeries={filteredSummary.sentiment_series}
                                onDateClick={handleDateClick}
                            />
                        </div>
                    </div>

                    <div className="grid gap-6 lg:grid-cols-2 mt-6">
                        {/* Returns */}
                        <div className="lg:h-[400px]">
                            <ReturnsChart 
                                priceSeries={filteredSummary.price_series} 
                                syncId={SYNC_ID}
                                onDateHover={setHoveredDate}
                                onDateClick={handleDateClick}
                            />
                        </div>

                        {/* Distribution */}
                        <div className="lg:h-[400px]">
                            <SentimentDistributionChart 
                                articles={filteredSummary.articles} 
                                onBucketClick={(bucket: any) => setSelectedSentimentBucket(bucket)}
                            />
                        </div>
                    </div>
                </section>

                {/* 3. News Drivers Section */}
                <div ref={newsSectionRef} className="mb-12 scroll-mt-24">
                    <NewsDriversSection 
                        articles={filteredSummary.articles}
                        priceSeries={filteredSummary.price_series}
                        selectedDate={selectedDate || hoveredDate}
                        selectedSentimentBucket={selectedSentimentBucket}
                    />
                </div>
            </>
        )}

        {/* 4. Model Reliability */}
        <section className="mb-12">
            <ModelReliabilitySection />
        </section>

      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm">
            <p>Built with FastAPI, React, and Machine Learning.</p>
            <p className="mt-1">Not financial advice. For educational purposes only.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
