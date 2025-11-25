"""
FastAPI backend application.
"""
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from typing import List, Optional
from collections import defaultdict

from db import crud_supabase
from services.data_refresh import ensure_price_data, ensure_news_data, enrich_sentiment_for_new_articles
from services.model_inference import get_model_inference
from utils.date_helpers import get_last_30_days_range
from schemas import (
    TickerResponse,
    SummaryResponse,
    PricePoint,
    SentimentPoint,
    ArticleResponse,
    ModelInsights,
    ModelMetricsResponse
)

app = FastAPI(title="News & Sentiment Driven Stock Explorer API")

# CORS configuration - configurable via environment variable
# Defaults include localhost for development and common Vercel patterns
default_origins = [
    "http://localhost:5173",  # Vite default dev port
    "http://localhost:3000",  # Alternative dev port
    "https://news-sentiment-driven-stock-explore.vercel.app",  # Production Vercel domain
]

# Parse ALLOWED_ORIGINS from environment (comma-separated list)
# For production, set this to your Vercel domain(s), e.g.:
# ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-preview.vercel.app
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    # Split by comma and strip whitespace
    origins = [origin.strip() for origin in allowed_origins_env.split(",")]
    # Remove trailing slashes and empty strings
    origins = [o.rstrip('/') for o in origins if o]
    # Remove empty strings after stripping
    origins = [o for o in origins if o]
    # Merge with defaults to ensure localhost is always available for dev
    origins = list(set(origins + default_origins))
else:
    origins = default_origins

# Log origins for debugging
print(f"CORS allowed origins: {origins}")

# CORS middleware configuration
# Using allow_origin_regex to match any *.vercel.app domain for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow any Vercel deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tickers", response_model=List[TickerResponse])
async def get_tickers():
    """Get list of available tickers."""
    tickers = crud_supabase.get_tickers()
    return [TickerResponse(symbol=t["symbol"], name=t.get("name")) for t in tickers]


@app.get("/api/summary", response_model=SummaryResponse)
async def get_summary(
    ticker: str = Query(..., description="Stock ticker symbol"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD). Defaults to 30 days ago."),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD). Defaults to today.")
):
    """
    Get summary data for a ticker and date range.
    Ensures data is fresh by checking cache and fetching from APIs if needed.
    
    If start_date or end_date are not provided, defaults to last 30 days.
    """
    # Default to last 30 days if dates not provided, but check available data first
    if start_date is None or end_date is None:
        # Try to detect available date range from database
        latest_date = crud_supabase.get_latest_price_date(ticker)
        earliest_date = crud_supabase.get_earliest_price_date(ticker)
        
        if latest_date and earliest_date:
            # Use available data range, but cap to today
            today = date.today()
            detected_end = min(latest_date, today)
            detected_start = earliest_date
            
            # If no dates provided, use detected range
            if start_date is None:
                start_date = detected_start
            if end_date is None:
                end_date = detected_end
            
            # If dates provided but out of range, adjust
            if start_date > detected_end:
                start_date = detected_start
            if end_date > detected_end:
                end_date = detected_end
            if end_date < detected_start:
                end_date = detected_end
        else:
            # No data in DB, use default 30 days
            default_start, default_end = get_last_30_days_range()
            start_date = start_date or default_start
            end_date = end_date or default_end
    
    # Cap dates to today - cannot fetch future data
    today = date.today()
    if end_date > today:
        end_date = today
    if start_date > today:
        start_date = today - timedelta(days=365)
    
    # Ensure valid date range
    if start_date >= end_date:
        start_date = end_date - timedelta(days=365)
    
    # Validate ticker exists
    ticker_obj = crud_supabase.get_ticker_by_symbol(ticker)
    if not ticker_obj:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    
    # Ensure price data is fresh (with error handling)
    try:
        ensure_price_data(ticker, start_date, end_date)
    except Exception as e:
        print(f"Warning: Error ensuring price data for {ticker}: {e}")
        # Continue anyway - we'll use what we have
    
    # Ensure news data is fresh (with error handling)
    # NOTE: ensure_news_data() is conservative - only fetches last 2 days if missing
    # For large backfills, use the dedicated script: backend/scripts/backfill_news.py
    new_articles_count = 0
    try:
        new_articles_count = ensure_news_data(ticker, start_date, end_date, ticker_obj.get("name"))
    except Exception as e:
        print(f"Warning: Error ensuring news data for {ticker}: {e}")
        # Continue anyway - we'll use what we have
    
    # Enrich sentiment for any new articles
    if new_articles_count > 0:
        try:
            enrich_sentiment_for_new_articles(batch_size=50)
        except Exception as e:
            print(f"Warning: Error enriching sentiment: {e}")
            # Continue anyway
    
    # Get price data
    prices = crud_supabase.get_prices(ticker, start_date, end_date)
    price_series = []
    for p in prices:
        try:
            # Handle both string and date objects
            price_date = p["date"]
            if isinstance(price_date, str):
                price_date = date.fromisoformat(price_date)
            elif isinstance(price_date, date):
                pass  # Already a date
            else:
                # Try to parse as datetime
                if isinstance(price_date, datetime):
                    price_date = price_date.date()
                else:
                    continue  # Skip invalid dates
            
            price_series.append(
                PricePoint(date=price_date, close=float(p["close"]))
            )
        except Exception as e:
            print(f"Error parsing price data: {e}, skipping entry")
            continue
    
    # Get articles (only relevant ones)
    articles = crud_supabase.get_articles(ticker, start_date, end_date, relevant_only=True)
    
    # Debug: Log sentiment distribution
    sentiment_scores = [float(a["sentiment_score"]) for a in articles if a.get("sentiment_score") is not None]
    if sentiment_scores:
        negative_count = sum(1 for s in sentiment_scores if s < -0.1)
        positive_count = sum(1 for s in sentiment_scores if s > 0.1)
        neutral_count = len(sentiment_scores) - negative_count - positive_count
        
        # Also count by label
        label_counts = {}
        for a in articles:
            label = a.get("sentiment_label")
            if label:
                label_counts[label] = label_counts.get(label, 0) + 1
        
        print(f"[DEBUG] {ticker} sentiment distribution: {len(sentiment_scores)} articles, "
              f"negative: {negative_count}, neutral: {neutral_count}, positive: {positive_count}")
        if label_counts:
            print(f"[DEBUG] {ticker} sentiment labels: {label_counts}")
    
    # Compute daily sentiment averages
    daily_sentiment = defaultdict(list)
    for article in articles:
        sentiment_score = article.get("sentiment_score")
        if sentiment_score is not None:
            try:
                pub_date_str = article["published_at"]
                pub_date = None
                
                if isinstance(pub_date_str, str):
                    # Extract date part (before T or space)
                    date_part = pub_date_str.split("T")[0].split(" ")[0]
                    # Parse as date (YYYY-MM-DD format)
                    pub_date = date.fromisoformat(date_part)
                elif isinstance(pub_date_str, date):
                    pub_date = pub_date_str
                elif isinstance(pub_date_str, datetime):
                    pub_date = pub_date_str.date()
                
                if pub_date:
                    daily_sentiment[pub_date].append(float(sentiment_score))
            except Exception as e:
                print(f"Error parsing article date: {e}, article_id: {article.get('id')}, date_str: {pub_date_str}")
                continue
    
    
    sentiment_series = [
        SentimentPoint(date=d, sentiment_avg=sum(scores) / len(scores))
        for d, scores in sorted(daily_sentiment.items())
    ]
    
    # Calculate average sentiment (weighted by relevance_score if available)
    all_sentiments = []
    for a in articles:
        sentiment_score = a.get("sentiment_score")
        if sentiment_score is not None:
            # Use relevance_score as weight if available
            relevance = float(a.get("relevance_score", 1.0)) if a.get("relevance_score") is not None else 1.0
            all_sentiments.append((float(sentiment_score), relevance))
    
    if all_sentiments:
        # Weighted average
        total_weight = sum(weight for _, weight in all_sentiments)
        if total_weight > 0:
            avg_sentiment = sum(score * weight for score, weight in all_sentiments) / total_weight
        else:
            avg_sentiment = sum(score for score, _ in all_sentiments) / len(all_sentiments)
    else:
        avg_sentiment = 0.0
    
    # Format articles
    article_responses = []
    for a in articles:
        try:
            pub_date_str = a["published_at"]
            pub_date = None
            
            if isinstance(pub_date_str, str):
                # Extract just the date part (YYYY-MM-DD) - same as sentiment parsing
                date_part = pub_date_str.split("T")[0].split(" ")[0]
                pub_date = date.fromisoformat(date_part)
            elif isinstance(pub_date_str, date):
                pub_date = pub_date_str
            elif isinstance(pub_date_str, datetime):
                pub_date = pub_date_str.date()
            
            if pub_date:
                article_responses.append(
                    ArticleResponse(
                        date=pub_date,
                        headline=a.get("headline", ""),
                        source=a.get("source", "Unknown"),
                        url=a.get("url"),
                        sentiment_score=float(a["sentiment_score"]) if a.get("sentiment_score") is not None else None,
                        sentiment_label=a.get("sentiment_label")
                    )
                )
        except Exception as e:
            print(f"Error formatting article {a.get('id')}: {e}, date_str: {pub_date_str}")
            continue
    
    
    # Get model insights
    model_insights = None
    model_inference = get_model_inference()
    if model_inference.model is not None:
        try:
            prob_df = model_inference.predict_probabilities(prices, articles)
            if prob_df is not None and len(prob_df) > 0:
                mean_prob = float(prob_df["prob_positive_return"].mean())
                metrics = model_inference.get_metrics()
                baseline_rate = metrics.get("baseline_accuracy", 0.5)
                
                # Generate comment
                if mean_prob > baseline_rate + 0.1:
                    comment = f"During this period, sentiment was predictive of positive returns. The model suggests a {mean_prob:.1%} average probability of positive 3-day returns, compared to a baseline of {baseline_rate:.1%}."
                elif mean_prob < baseline_rate - 0.1:
                    comment = f"During this period, sentiment was predictive of negative returns. The model suggests a {mean_prob:.1%} average probability of positive 3-day returns, compared to a baseline of {baseline_rate:.1%}."
                else:
                    comment = f"During this period, sentiment showed modest predictive power. The model suggests a {mean_prob:.1%} average probability of positive 3-day returns, similar to the baseline of {baseline_rate:.1%}."
                
                model_insights = ModelInsights(
                    mean_positive_prob=mean_prob,
                    baseline_positive_rate=baseline_rate,
                    comment=comment
                )
        except Exception as e:
            print(f"Error computing model insights: {e}")
    
    # Ensure we have at least some data
    if len(price_series) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for {ticker} in date range {start_date} to {end_date}"
        )
    
    return SummaryResponse(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        n_articles=len(articles),
        avg_sentiment=avg_sentiment,
        price_series=price_series,
        sentiment_series=sentiment_series,
        articles=article_responses,
        model_insights=model_insights
    )


@app.get("/api/model-metrics", response_model=ModelMetricsResponse)
async def get_model_metrics():
    """
    Get model training metrics.
    
    Returns metrics from the primary model (logistic regression by default).
    Includes comprehensive metrics if available from the new training pipeline.
    """
    # Try to load logistic regression metrics first (primary model)
    from pathlib import Path
    import json
    
    models_dir = Path(__file__).parent / "models"
    log_reg_metrics_path = models_dir / "log_reg_metrics.json"
    
    metrics = {}
    
    # Prefer logistic regression metrics if available
    if log_reg_metrics_path.exists():
        try:
            with open(log_reg_metrics_path, "r") as f:
                metrics = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load log_reg_metrics.json: {e}")
    
    # Fall back to primary metrics or model inference metrics
    if not metrics:
        model_inference = get_model_inference()
        metrics = model_inference.get_metrics()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Model metrics not found. Train the model first.")
    
    # Ensure backward compatibility: map 'roc_auc' to 'auc' if needed
    if "roc_auc" in metrics and "auc" not in metrics:
        metrics["auc"] = metrics["roc_auc"]
    # Also set roc_auc if only auc exists
    if "auc" in metrics and "roc_auc" not in metrics:
        metrics["roc_auc"] = metrics["auc"]
    
    # Map 'n_test' to 'n_samples' for backward compatibility
    if "n_test" in metrics and "n_samples" not in metrics:
        metrics["n_samples"] = metrics["n_test"]
    
    return ModelMetricsResponse(**metrics)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "News & Sentiment Driven Stock Explorer API"}


@app.get("/health")
@app.get("/healthz")
async def health_check():
    """
    Health check endpoint for deployment platforms (e.g., Render).
    Returns a simple status response.
    """
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    """Initialize model inference on startup."""
    get_model_inference()
    print("Model inference service initialized")
