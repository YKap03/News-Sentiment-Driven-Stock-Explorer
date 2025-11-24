"""
Pydantic models for API request/response schemas.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date, datetime


class TickerResponse(BaseModel):
    """Ticker information."""
    symbol: str
    name: Optional[str] = None


class PricePoint(BaseModel):
    """Price data point."""
    date: date
    close: float


class SentimentPoint(BaseModel):
    """Sentiment data point."""
    date: date
    sentiment_avg: float


class ArticleResponse(BaseModel):
    """News article response."""
    date: date
    headline: str
    source: str
    url: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None


class ModelInsights(BaseModel):
    """ML model insights."""
    mean_positive_prob: float
    baseline_positive_rate: float
    comment: str


class SummaryResponse(BaseModel):
    """Summary response for a ticker and date range."""
    ticker: str
    start_date: date
    end_date: date
    n_articles: int
    avg_sentiment: float
    price_series: List[PricePoint]
    sentiment_series: List[SentimentPoint]
    articles: List[ArticleResponse]
    model_insights: Optional[ModelInsights] = None


class ModelMetricsResponse(BaseModel):
    """Model metrics response."""
    accuracy: float
    baseline_accuracy: float
    auc: Optional[float] = None
    roc_auc: Optional[float] = None  # Alias for auc
    balanced_accuracy: Optional[float] = None
    n_samples: Optional[int] = None  # For backward compatibility
    train_start_date: Optional[str] = None
    train_end_date: Optional[str] = None
    n_tickers: Optional[int] = None
    feature_names: Optional[List[str]] = None
    # New comprehensive metrics
    model_type: Optional[str] = None
    train_accuracy: Optional[float] = None
    precision_pos: Optional[float] = None
    recall_pos: Optional[float] = None
    f1_pos: Optional[float] = None
    precision_neg: Optional[float] = None
    recall_neg: Optional[float] = None
    f1_neg: Optional[float] = None
    n_train: Optional[int] = None
    n_test: Optional[int] = None
    class_distribution_train: Optional[Dict[str, int]] = None
    class_distribution_test: Optional[Dict[str, int]] = None
    test_start_date: Optional[str] = None
    test_end_date: Optional[str] = None
    best_C: Optional[float] = None
    decision_threshold: Optional[float] = None

