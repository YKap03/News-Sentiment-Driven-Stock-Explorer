"""
Feature engineering for ML model.
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import date, timedelta
from db.models import DailyPrice, NewsArticle


def compute_features(
    prices: List[dict],
    articles: List[dict]
) -> pd.DataFrame:
    """
    Compute ML features from price and article data.
    
    Args:
        prices: List of DailyPrice objects
        articles: List of NewsArticle objects
        
    Returns:
        DataFrame with columns: date, sentiment_avg, sentiment_rolling_mean_3d,
        return_1d, volatility_5d, future_3d_return_positive
    """
    # Convert to DataFrames
    from datetime import datetime, date as date_type
    
    prices_df = pd.DataFrame([
        {
            "date": date_type.fromisoformat(p["date"]) if isinstance(p["date"], str) else p["date"],
            "close": float(p["close"]),
            "ticker_symbol": p["ticker_symbol"]
        }
        for p in prices
    ])
    
    if not len(prices_df):
        return pd.DataFrame()
    
    # Filter articles: only use relevant articles with sentiment scores
    # Include relevance_score for weighted averaging
    articles_df = pd.DataFrame([
        {
            "date": datetime.fromisoformat(a["published_at"].replace("Z", "+00:00")).date() if isinstance(a["published_at"], str) else a["published_at"].date(),
            "sentiment_score": float(a["sentiment_score"]) if a.get("sentiment_score") is not None else None,
            "relevance_score": float(a.get("relevance_score", 1.0)) if a.get("relevance_score") is not None else 1.0,  # Default to 1.0 if not set
            "ticker_symbol": a["ticker_symbol"]
        }
        for a in articles 
        if a.get("sentiment_score") is not None 
        and a.get("is_relevant", True)  # Only use relevant articles
    ])
    
    # Sort by date
    prices_df = prices_df.sort_values("date").reset_index(drop=True)
    
    # Compute returns
    prices_df["return_1d"] = prices_df["close"].pct_change()
    
    # Compute volatility (rolling 5-day std of returns)
    prices_df["volatility_5d"] = prices_df["return_1d"].rolling(window=5, min_periods=1).std()
    
    # Aggregate sentiment by date using weighted average (weighted by relevance_score)
    if len(articles_df):
        # Compute weighted average: sum(sentiment * relevance) / sum(relevance)
        articles_df["weighted_sentiment"] = articles_df["sentiment_score"] * articles_df["relevance_score"]
        
        daily_sentiment = articles_df.groupby("date").agg({
            "weighted_sentiment": "sum",
            "relevance_score": "sum"
        }).reset_index()
        
        # Calculate weighted average
        daily_sentiment["sentiment_avg"] = (
            daily_sentiment["weighted_sentiment"] / daily_sentiment["relevance_score"]
        ).fillna(0.0)
        
        daily_sentiment = daily_sentiment[["date", "sentiment_avg"]]
    else:
        daily_sentiment = pd.DataFrame(columns=["date", "sentiment_avg"])
    
    # Merge sentiment into prices
    features_df = prices_df.merge(daily_sentiment, on="date", how="left")
    features_df["sentiment_avg"] = features_df["sentiment_avg"].fillna(0.0)
    
    # Compute rolling mean of sentiment (3 days)
    features_df["sentiment_rolling_mean_3d"] = (
        features_df["sentiment_avg"].rolling(window=3, min_periods=1).mean()
    )
    
    # Compute future 3-day return
    features_df["future_3d_return"] = (
        features_df["close"].shift(-3) / features_df["close"] - 1.0
    )
    features_df["future_3d_return_positive"] = (
        (features_df["future_3d_return"] > 0).astype(int)
    )
    
    # Select and return feature columns
    feature_cols = [
        "date",
        "sentiment_avg",
        "sentiment_rolling_mean_3d",
        "return_1d",
        "volatility_5d",
        "future_3d_return_positive"
    ]
    
    result = features_df[feature_cols].copy()
    
    # Drop rows with NaN target (last 3 days won't have future return)
    result = result.dropna(subset=["future_3d_return_positive"])
    
    return result


def prepare_training_data(features_df: pd.DataFrame) -> tuple:
    """
    Prepare features and target for model training.
    
    Args:
        features_df: DataFrame from compute_features
        
    Returns:
        (X, y) tuple where X is feature matrix and y is target vector
    """
    feature_cols = [
        "sentiment_avg",
        "sentiment_rolling_mean_3d",
        "return_1d",
        "volatility_5d"
    ]
    
    X = features_df[feature_cols].fillna(0.0).values
    y = features_df["future_3d_return_positive"].values
    
    return X, y

