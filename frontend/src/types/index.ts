/**
 * TypeScript types matching backend API schemas.
 */

export interface Ticker {
  symbol: string;
  name: string | null;
}

export interface PricePoint {
  date: string; // ISO date string
  close: number;
}

export interface SentimentPoint {
  date: string; // ISO date string
  sentiment_avg: number;
}

export interface Article {
  date: string; // ISO date string
  headline: string;
  source: string;
  url: string | null;
  sentiment_score: number | null;
  sentiment_label: string | null;
}

export interface ModelInsights {
  mean_positive_prob: number;
  baseline_positive_rate: number;
  comment: string;
}

export interface SummaryResponse {
  ticker: string;
  start_date: string;
  end_date: string;
  n_articles: number;
  avg_sentiment: number;
  price_series: PricePoint[];
  sentiment_series: SentimentPoint[];
  articles: Article[];
  model_insights: ModelInsights | null;
}

export interface ModelMetrics {
  accuracy: number;
  baseline_accuracy: number;
  auc: number | null;
  roc_auc?: number | null;
  balanced_accuracy?: number | null;
  n_samples: number;
  n_train?: number | null;
  n_test?: number | null;
  train_start_date: string;
  train_end_date: string;
  test_start_date?: string | null;
  test_end_date?: string | null;
  n_tickers: number | null;
  feature_names: string[] | null;
  best_C?: number | null;
  decision_threshold?: number | null;
}

