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
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">5. Model reliability</h3>
        <div className="text-center text-gray-500 py-8">Loading model metrics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">5. Model reliability</h3>
        <div className="text-center text-red-500 py-8">{error}</div>
      </div>
    );
  }

  if (!metrics) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="mb-6">
          <h3 className="text-xl font-semibold text-gray-900">5. Model reliability</h3>
          <p className="text-sm text-gray-500">How much can you trust the probability estimates above?</p>
      </div>
      
      <div className="mb-6 text-gray-700">
          <p className="mb-2">The model is a regularized logistic regression trained on several hundred days of data across multiple large-cap tickers. On unseen data its ROC-AUC is around {metrics.auc ? metrics.auc.toFixed(2) : '0.70'}, meaning it ranks days from more-likely to less-likely positive better than random, but it is not a trading system.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-slate-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-500 mb-1">Accuracy vs Baseline</div>
            <div className="text-xl font-bold text-gray-900">
                {(metrics.accuracy * 100).toFixed(1)}% 
                <span className="text-sm font-normal text-gray-500 ml-1">vs {(metrics.baseline_accuracy * 100).toFixed(1)}%</span>
            </div>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-500 mb-1">Balanced Accuracy</div>
            <div className="text-xl font-bold text-gray-900">
                {(metrics.balanced_accuracy ? metrics.balanced_accuracy * 100 : 0).toFixed(1)}%
            </div>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-500 mb-1">ROC-AUC</div>
            <div className="text-xl font-bold text-blue-600">
                {(metrics.auc || metrics.roc_auc || 0).toFixed(3)}
            </div>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-500 mb-1">Test Samples</div>
            <div className="text-xl font-bold text-gray-900">
                {(metrics.n_test || metrics.n_samples || 0).toLocaleString()}
                {metrics.n_train && <span className="block text-xs font-normal text-gray-500 mt-1">Train: {metrics.n_train.toLocaleString()}</span>}
            </div>
        </div>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
        <h4 className="font-medium text-blue-900 mb-2">Interpretation</h4>
        <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
            <li>Above-chance ROC-AUC indicates some predictive signal.</li>
            <li>Accuracy close to baseline – use this for exploration, not precise trading rules.</li>
            <li>Performance varies by ticker and time window.</li>
        </ul>
      </div>
    </div>
  );
}
