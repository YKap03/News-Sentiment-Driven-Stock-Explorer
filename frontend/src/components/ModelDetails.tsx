import { useEffect, useState } from 'react';
import { getModelMetrics } from '../api/client';
import type { ModelMetrics } from '../types';
import { format, parseISO } from 'date-fns';

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
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Model Details</h3>
        <div className="text-center text-gray-500 py-8">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Model Details</h3>
        <div className="text-center text-red-500 py-8">{error}</div>
      </div>
    );
  }

  if (!metrics) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">ML Model Details</h3>
      <div className="space-y-4">
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Model Performance</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-500">Accuracy</div>
              <div className="text-xl font-semibold text-gray-900">
                {(metrics.accuracy * 100).toFixed(1)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Baseline</div>
              <div className="text-xl font-semibold text-gray-600">
                {(metrics.baseline_accuracy * 100).toFixed(1)}%
              </div>
            </div>
            {metrics.balanced_accuracy !== undefined && metrics.balanced_accuracy !== null && (
              <div>
                <div className="text-sm text-gray-500">Balanced Accuracy</div>
                <div className="text-xl font-semibold text-gray-900">
                  {(metrics.balanced_accuracy * 100).toFixed(1)}%
                </div>
              </div>
            )}
            {(metrics.auc || metrics.roc_auc) && (
              <div>
                <div className="text-sm text-gray-500">ROC-AUC</div>
                <div className="text-xl font-semibold text-gray-900">
                  {(metrics.auc || metrics.roc_auc || 0).toFixed(3)}
                </div>
              </div>
            )}
          </div>
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-500">Test Samples</div>
              <div className="text-xl font-semibold text-gray-900">
                {(metrics.n_test || metrics.n_samples || 0).toLocaleString()}
              </div>
            </div>
            {metrics.n_train && (
              <div>
                <div className="text-sm text-gray-500">Train Samples</div>
                <div className="text-xl font-semibold text-gray-900">
                  {metrics.n_train.toLocaleString()}
                </div>
              </div>
            )}
          </div>
        </div>

        <div>
          <h4 className="font-medium text-gray-700 mb-2">Training Period</h4>
          <div className="text-sm text-gray-600">
            {format(parseISO(metrics.train_start_date), 'MMM d, yyyy')} -{' '}
            {format(parseISO(metrics.train_end_date), 'MMM d, yyyy')}
            {metrics.n_tickers && ` (${metrics.n_tickers} tickers)`}
          </div>
        </div>

        {metrics.feature_names && metrics.feature_names.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Features</h4>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              {metrics.feature_names.map((feature, idx) => (
                <li key={idx}>{feature}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            <strong>What this model does:</strong> This RandomForest classifier predicts the
            probability of a positive 3-day return based on sentiment and price features.
            It was trained on historical data and uses features like daily sentiment averages,
            rolling sentiment means, returns, and volatility.
          </p>
        </div>
      </div>
    </div>
  );
}

