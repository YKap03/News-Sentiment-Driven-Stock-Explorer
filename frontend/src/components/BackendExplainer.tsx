import { IconDatabase, IconCpu, IconBarChart, IconGlobe } from './Icons';

export default function BackendExplainer() {
  const steps = [
    {
      icon: IconGlobe,
      title: "1. Data Ingestion",
      desc: "We fetch real-time news from Alpha Vantage and stock prices from Yahoo Finance. A bespoke scraper filters out noise like spam, legal alerts, and generic market reports."
    },
    {
      icon: IconDatabase,
      title: "2. Smart Caching",
      desc: "To optimize performance and respect API limits, all valid data is cached in a Supabase Postgres database. We only fetch what's new."
    },
    {
      icon: IconCpu,
      title: "3. Feature Engineering",
      desc: "Raw text is converted into sentiment scores. We calculate rolling averages, volatility, and momentum indicators to prepare the dataset for ML."
    },
    {
      icon: IconBarChart,
      title: "4. Predictive Modeling",
      desc: "A trained RandomForest Classifier analyzes the features to predict the probability of positive 3-day returns, comparing it against a statistical baseline."
    }
  ];

  return (
    <section className="mb-16 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-slate-50 to-white opacity-50 pointer-events-none" />
      <div className="relative z-10">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight mb-3">
            How It Works Under the Hood
          </h2>
          <p className="text-slate-500 max-w-2xl mx-auto">
            This isn't just a UI wrapper. It's a full-stack data science pipeline running on modern infrastructure.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, idx) => (
            <div key={idx} className="glass-card p-6 border-t-4 border-t-blue-500/20 hover:border-t-blue-600 transition-all">
              <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600 mb-4 shadow-sm">
                <step.icon className="w-6 h-6" />
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">{step.title}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

