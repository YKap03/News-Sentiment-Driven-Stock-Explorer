"""
Offline ML model training script.
Trains a classifier to predict positive 3-day returns based on sentiment and price features.
"""
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db import crud_supabase
from services.feature_engineering import compute_features, prepare_training_data


def train_model(
    tickers: list = None,
    start_date: date = None,
    end_date: date = None,
    test_size: float = 0.2
):
    """
    Train ML model on historical data.
    
    Args:
        tickers: List of ticker symbols to use for training (default: all in DB)
        start_date: Start date for training data (default: 1 year ago)
        end_date: End date for training data (default: today)
        test_size: Fraction of data to use for testing
    """
    # Handle incorrect system dates (if system date is in future)
    system_today = date.today()
    if system_today.year >= 2025:
        # System date is wrong, use a reasonable recent date
        today = date(2024, 11, 20)
        print(f"[NOTE] System date appears incorrect ({system_today}), using {today} instead")
    else:
        today = system_today
    
    # Use all available data by default (don't restrict by dates)
    # This ensures we use all the data we have in the database
    if start_date is None:
        start_date = date(2020, 1, 1)  # Query from 2020 to get all historical data
    if end_date is None:
        end_date = today
    
    print(f"Training model - querying data from {start_date} to {end_date}")
    print(f"[NOTE] Will use ALL available data in database for training")
    
    try:
        # Get tickers
        if tickers is None:
            all_tickers = crud_supabase.get_tickers()
            tickers = [t["symbol"] for t in all_tickers]
        
        if not tickers:
            print("No tickers found. Please add tickers to the database first.")
            return
        
        print(f"Using tickers: {', '.join(tickers)}")
        
        # Collect features from all tickers
        all_features = []
        
        for ticker_symbol in tickers:
            print(f"Processing {ticker_symbol}...")
            
            # Get prices - use the date range specified (or all available)
            prices = crud_supabase.get_prices_sync(ticker_symbol, start_date, end_date)
            if not prices:
                print(f"  No price data for {ticker_symbol}")
                continue
            
            # Get articles - use same date range
            articles = crud_supabase.get_articles_sync(ticker_symbol, start_date, end_date)
            print(f"  Found {len(prices)} price records, {len(articles)} articles")
            
            # Compute features
            features_df = compute_features(prices, articles)
            if len(features_df) > 0:
                features_df["ticker_symbol"] = ticker_symbol
                all_features.append(features_df)
        
        if not all_features:
            print("No features computed. Check data availability.")
            return
        
        # Combine all features
        combined_features = pd.concat(all_features, ignore_index=True)
        print(f"\nTotal feature rows: {len(combined_features)}")
        
        # Prepare training data
        X, y = prepare_training_data(combined_features)
        
        print(f"Feature matrix shape: {X.shape}")
        print(f"Target distribution: {np.bincount(y)}")
        
        # Split into train/test (time-based split would be better, but simple split for now)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Train model
        print("\nTraining RandomForestClassifier...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        
        baseline_acc = max(np.bincount(y_test)) / len(y_test)
        
        # ROC-AUC if possible
        try:
            test_proba = model.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, test_proba)
        except:
            auc = None
        
        print(f"\nTraining accuracy: {train_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        print(f"Baseline accuracy: {baseline_acc:.4f}")
        if auc:
            print(f"Test ROC-AUC: {auc:.4f}")
        
        # Save model
        models_dir = Path(__file__).parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        model_path = models_dir / "classifier.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"\nModel saved to {model_path}")
        
        # Save metrics
        metrics = {
            "accuracy": float(test_acc),
            "baseline_accuracy": float(baseline_acc),
            "auc": float(auc) if auc else None,
            "n_samples": int(len(combined_features)),
            "train_start_date": start_date.isoformat(),
            "train_end_date": end_date.isoformat(),
            "n_tickers": len(tickers),
            "feature_names": [
                "sentiment_avg",
                "sentiment_rolling_mean_3d",
                "return_1d",
                "volatility_5d"
            ]
        }
        
        metrics_path = models_dir / "model_metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"Metrics saved to {metrics_path}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Default: train on all tickers with last 30 days of data
    # You can customize by passing tickers and dates
    from utils.date_helpers import get_last_30_days_range
    
    default_start, default_end = get_last_30_days_range()
    train_model(
        tickers=None,  # None = use all tickers in database
        start_date=default_start,  # Last 30 days
        end_date=default_end
    )
