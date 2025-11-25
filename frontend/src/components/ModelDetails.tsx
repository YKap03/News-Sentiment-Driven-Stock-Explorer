import { useEffect, useState } from 'react';
import { getModelMetrics } from '../api/client';
import type { ModelMetrics } from '../types';

export default function ModelDetails() {
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadMetrics() {
      try {
        setLoading(true);
        const data = await getModelMetrics();
        setMetrics(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load model metrics');
      } finally {
        setLoading(false);
      }
    }
    loadMetrics();
  }, []);

  if (loading) {
    return (
      <div className="glass-card p-8 animate-pulse">
        <div className="h-6 bg-slate-200 rounded w-1/3 mb-4"></div>
        <div className="h-20 bg-slate-100 rounded mb-6"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-8 border-red-200">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  if (!metrics) return null;

  return (
    <div className="glass-card p-8 bg-gradient-to-br from-slate-50 to-white">
      <div className="mb-8">
          <h3 className="text-2xl font-bold text-slate-900 mb-2">5. Model Reliability & Trust</h3>
          <p className="text-slate-500 max-w-3xl">
            We believe in radical transparency. Our predictions are powered by a regularized logistic regression model trained on historical data. Here's exactly how it performs on unseen test data.
          </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center text-center hover:shadow-md transition-shadow">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Accuracy</div>
            <div className="text-3xl font-extrabold text-slate-900 mb-1">
                {(metrics.accuracy * 100).toFixed(1)}% 
            </div>
            <div className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                vs {(metrics.baseline_accuracy * 100).toFixed(1)}% baseline
            </div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center text-center hover:shadow-md transition-shadow">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Balanced Accuracy</div>
            <div className="text-3xl font-extrabold text-indigo-600 mb-1">
                {(metrics.balanced_accuracy ? metrics.balanced_accuracy * 100 : 0).toFixed(1)}%
            </div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center text-center hover:shadow-md transition-shadow">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">ROC-AUC Score</div>
            <div className="text-3xl font-extrabold text-blue-600 mb-1">
                {(metrics.auc || metrics.roc_auc || 0).toFixed(3)}
            </div>
            <div className="text-xs text-blue-600/80">
                {metrics.auc && metrics.auc > 0.5 ? 'Better than random' : 'Random'}
            </div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center text-center hover:shadow-md transition-shadow">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Test Samples</div>
            <div className="text-3xl font-extrabold text-slate-900 mb-1">
                {(metrics.n_test || metrics.n_samples || 0).toLocaleString()}
            </div>
            {metrics.n_train && <div className="text-xs text-slate-400">Trained on {metrics.n_train.toLocaleString()}</div>}
        </div>
      </div>

      <div className="bg-blue-50/50 border border-blue-100 rounded-xl p-6">
        <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            How to Interpret These Numbers
        </h4>
        <ul className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-800/80">
            <li className="flex items-start gap-2">
                <span className="mt-1 w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0"></span>
                <span><strong>ROC-AUC &gt; 0.5</strong> indicates the model finds real predictive signal in the sentiment data.</span>
            </li>
            <li className="flex items-start gap-2">
                <span className="mt-1 w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0"></span>
                <span><strong>Accuracy</strong> should be compared to the baseline. If we beat the baseline, sentiment adds value.</span>
            </li>
            <li className="flex items-start gap-2">
                <span className="mt-1 w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0"></span>
                <span>This is a <strong>probabilistic tool</strong> for idea generation, not a standalone trading system.</span>
            </li>
        </ul>
      </div>
    </div>
  );
}
