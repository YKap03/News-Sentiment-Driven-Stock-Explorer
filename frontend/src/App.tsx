import { useState, useMemo, useRef } from 'react';
import ControlsSection from './components/ControlsSection';
import SummaryBar from './components/SummaryBar';
import PriceSentimentChart from './components/PriceSentimentChart';
import CorrelationChart from './components/CorrelationChart';
import ReturnsChart from './components/ReturnsChart';
import SentimentDistributionChart from './components/SentimentDistributionChart';
import NewsDriversSection from './components/NewsDriversSection';
import ModelReliabilitySection from './components/ModelDetails';
import BackendExplainer from './components/BackendExplainer';
import { getSummary } from './api/client';
import type { SummaryResponse } from './types';
import { IconTrendingUp, IconZap } from './components/Icons';

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
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-blue-100 text-slate-900">
       {/* Decorative Background Elements */}
       <div className="fixed inset-0 pointer-events-none overflow-hidden">
         <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-400/10 rounded-full blur-[100px]" />
         <div className="absolute top-[20%] right-[-10%] w-[40%] h-[40%] bg-indigo-400/10 rounded-full blur-[100px]" />
       </div>

       {/* New Hero Header */}
       <header className="relative bg-white/80 backdrop-blur-md border-b border-slate-200/50 sticky top-0 z-50">
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
                    <IconTrendingUp className="w-5 h-5" />
                </div>
                <span className="font-bold text-lg tracking-tight text-slate-900">StockSentiment<span className="text-blue-600">.AI</span></span>
            </div>
            <div className="text-xs font-medium px-3 py-1 bg-slate-100 rounded-full text-slate-600 border border-slate-200">
                v1.0.0 • Beta
            </div>
         </div>
       </header>

       <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
         
         {/* Hero Text */}
         <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-sm font-medium mb-6">
                <IconZap className="w-4 h-4" />
                <span>Powered by Advanced NLP & Random Forest</span>
            </div>
            <h1 className="text-4xl md:text-6xl font-extrabold text-slate-900 tracking-tight mb-6">
                Decode the Market with <br/>
                <span className="gradient-text">Sentiment Intelligence</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-500 max-w-2xl mx-auto leading-relaxed">
                Don't just watch the price. Understand the <strong>why</strong> behind the move using our institutional-grade sentiment analysis engine.
            </p>
         </div>

         {/* Backend Explainer Section */}
         <BackendExplainer />

         {/* Controls Section */}
         <div id="analyze" className="scroll-mt-24 relative z-10">
            <ControlsSection 
                ticker={ticker}
                startDate={startDate}
                endDate={endDate}
                loading={loading}
                onTickerChange={setTicker}
                // onStartDateChange={setStartDate} // Unused
                // onEndDateChange={setEndDate}     // Unused
                onAnalyze={handleAnalyze}
            />
         </div>

        {error && (
            <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-center shadow-sm">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
                {error}
            </div>
        )}

        {filteredSummary && (
            <div className="animate-fade-in">
                {/* 1.3 Insight Bar */}
                <SummaryBar data={filteredSummary} />

                {/* 2. Evidence Section */}
                <section className="mb-16">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="h-px flex-1 bg-slate-200"></div>
                        <h2 className="text-2xl font-bold text-slate-900">3. Evidence & Analysis</h2>
                        <div className="h-px flex-1 bg-slate-200"></div>
                    </div>

                    <div className="grid gap-8 lg:grid-cols-2">
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

                    <div className="grid gap-8 lg:grid-cols-2 mt-8">
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
                <div ref={newsSectionRef} className="mb-16 scroll-mt-24">
                    <NewsDriversSection 
                        articles={filteredSummary.articles}
                        priceSeries={filteredSummary.price_series}
                        selectedDate={selectedDate || hoveredDate}
                        selectedSentimentBucket={selectedSentimentBucket}
                    />
                </div>
            </div>
        )}

        {/* 4. Model Reliability */}
        <section className="mb-16">
            <ModelReliabilitySection />
        </section>

        {/* Footer */}
        <footer className="mt-24 border-t border-slate-200 pt-12 pb-8 text-center">
            <div className="flex items-center justify-center gap-2 mb-4 opacity-50">
                <IconTrendingUp className="w-6 h-6" />
            </div>
            <p className="text-slate-400 text-sm mb-4 max-w-md mx-auto">
                Built for the future of finance. This project demonstrates the power of combining unstructured news data with quantitative market signals.
            </p>
            <div className="flex justify-center gap-6 text-slate-400 text-xs font-medium uppercase tracking-wider">
                <span>FastAPI</span>
                <span>React</span>
                <span>Supabase</span>
                <span>Tailwind</span>
                <span>Sklearn</span>
            </div>
        </footer>
      </main>
    </div>
  );
}

export default App;
