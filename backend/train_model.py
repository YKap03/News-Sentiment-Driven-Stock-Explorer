"""
Offline ML model training script.

Trains multiple models to predict positive 3-day returns based on sentiment and price features.
Uses time-based train/test split to avoid data leakage.
Implements:
- Logistic Regression (regularized baseline)
- Random Forest (regularized)
- Comprehensive metrics and diagnostics

Usage:
    cd backend
    python train_model.py
"""
import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import pickle
import json
from typing import List, Optional, Tuple, Dict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.model_selection import TimeSeriesSplit

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db import crud_supabase
from services.feature_engineering import (
    compute_features,
    prepare_training_data,
    get_feature_names
)


# ============================================================================
# Configuration
# ============================================================================

# Default configuration
DEFAULT_TICKERS = None  # None = use all tickers in database
DEFAULT_START_DATE = date(2020, 1, 1)  # Query from 2020 to get all historical data
DEFAULT_END_DATE = None  # None = use today
DEFAULT_TEST_SIZE = 0.2  # 20% of data for testing
DEFAULT_LABEL_THRESHOLD = 0.0  # Threshold for positive label


# ============================================================================
# Time-based train/test split
# ============================================================================

def time_based_train_test_split(
    df: pd.DataFrame,
    date_col: str = "date",
    test_size: float = 0.2
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data into train and test sets based on date.
    
    Train: earliest (1 - test_size) fraction of dates
    Test: latest test_size fraction of dates
    
    Args:
        df: DataFrame with date column
        date_col: Name of date column
        test_size: Fraction of data to use for testing
        
    Returns:
        (train_df, test_df) tuple
    """
    # Sort by date
    df_sorted = df.sort_values(date_col).reset_index(drop=True)
    
    # Calculate split point
    n_total = len(df_sorted)
    n_test = int(n_total * test_size)
    n_train = n_total - n_test
    
    # Split: train = first n_train rows, test = remaining n_test rows
    train_df = df_sorted.iloc[:n_train].copy()
    test_df = df_sorted.iloc[n_train:].copy()
    
    return train_df, test_df


def compute_class_distribution(y: np.ndarray) -> Dict[str, int]:
    """
    Compute class distribution.
    
    Args:
        y: Target vector
        
    Returns:
        Dictionary with class counts
    """
    unique, counts = np.unique(y, return_counts=True)
    dist = {str(int(cls)): int(count) for cls, count in zip(unique, counts)}
    return dist


def compute_baseline_accuracy(y: np.ndarray) -> float:
    """
    Compute baseline accuracy (majority class frequency).
    
    Args:
        y: Target vector
        
    Returns:
        Baseline accuracy
    """
    if len(y) == 0:
        return 0.0
    unique, counts = np.unique(y, return_counts=True)
    return float(max(counts) / len(y))


# ============================================================================
# Model training functions
# ============================================================================

def train_logistic_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    random_state: int = 42
) -> Tuple[Pipeline, Dict]:
    """
    Train logistic regression model with C-tuning and threshold optimization.
    
    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        random_state: Random seed
        
    Returns:
        (model, metrics_dict) tuple
    """
    print("\n" + "="*60)
    print("Training Logistic Regression (Regularized Baseline)")
    print("="*60)
    
    # Step 1: C-tuning using TimeSeriesSplit
    print("\n--- C-tuning with TimeSeriesSplit ---")
    candidate_Cs = [0.01, 0.1, 1.0, 10.0]
    tscv = TimeSeriesSplit(n_splits=3)
    
    best_C = None
    best_score = -np.inf
    cv_results = []
    
    for C in candidate_Cs:
        fold_scores = []
        for train_idx, val_idx in tscv.split(X_train):
            X_tr, X_val = X_train[train_idx], X_train[val_idx]
            y_tr, y_val = y_train[train_idx], y_train[val_idx]
            
            pipe = Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(
                    C=C,
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=random_state,
                    n_jobs=-1,
                )),
            ])
            
            pipe.fit(X_tr, y_tr)
            val_proba = pipe.predict_proba(X_val)[:, 1]
            
            try:
                fold_score = roc_auc_score(y_val, val_proba)
            except ValueError:
                # Fallback to balanced accuracy at threshold 0.5
                val_pred = (val_proba >= 0.5).astype(int)
                fold_score = balanced_accuracy_score(y_val, val_pred)
            
            fold_scores.append(fold_score)
        
        mean_score = float(np.mean(fold_scores))
        cv_results.append({"C": C, "mean_score": mean_score})
        
        if mean_score > best_score:
            best_score = mean_score
            best_C = C
    
    # Print C-tuning summary
    print("C-tuning results:")
    for result in cv_results:
        marker = " <-- best" if result["C"] == best_C else ""
        print(f"  C={result['C']:6.2f}: mean_score={result['mean_score']:.4f}{marker}")
    print(f"Selected best_C: {best_C}")
    
    # Step 2: Threshold tuning on validation slice
    print("\n--- Threshold tuning for balanced accuracy ---")
    n_train = len(X_train)
    n_val = max(int(n_train * 0.2), 1)
    
    inner_train_idx = np.arange(0, n_train - n_val)
    val_idx = np.arange(n_train - n_val, n_train)
    
    X_inner_train, y_inner_train = X_train[inner_train_idx], y_train[inner_train_idx]
    X_val, y_val = X_train[val_idx], y_train[val_idx]
    
    # Fit temporary model on inner-train
    temp_model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            C=best_C,
            class_weight="balanced",
            max_iter=1000,
            random_state=random_state,
            n_jobs=-1,
        )),
    ])
    temp_model.fit(X_inner_train, y_inner_train)
    val_proba = temp_model.predict_proba(X_val)[:, 1]
    
    # Scan thresholds
    thresholds = np.linspace(0.2, 0.8, 13)  # 0.20, 0.25, ..., 0.80
    best_thr = 0.5
    best_thr_score = -np.inf
    
    for thr in thresholds:
        preds_val = (val_proba >= thr).astype(int)
        score = balanced_accuracy_score(y_val, preds_val)
        if score > best_thr_score:
            best_thr_score = score
            best_thr = thr
    
    print(f"Selected decision_threshold: {best_thr:.3f} (validation balanced accuracy: {best_thr_score:.4f})")
    
    # Step 3: Train final model on full training set
    print("\n--- Training final model ---")
    final_model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            C=best_C,
            class_weight="balanced",
            max_iter=1000,
            random_state=random_state,
            n_jobs=-1
        ))
    ])
    
    final_model.fit(X_train, y_train)
    
    # Step 4: Evaluate on test set using tuned threshold
    train_proba = final_model.predict_proba(X_train)[:, 1]
    test_proba = final_model.predict_proba(X_test)[:, 1]
    
    # Use tuned threshold for predictions
    train_pred = (train_proba >= best_thr).astype(int)
    test_pred = (test_proba >= best_thr).astype(int)
    
    # Metrics
    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, test_pred)
    train_bal_acc = balanced_accuracy_score(y_train, train_pred)
    test_bal_acc = balanced_accuracy_score(y_test, test_pred)
    baseline_acc = compute_baseline_accuracy(y_test)
    
    try:
        auc = roc_auc_score(y_test, test_proba)
    except:
        auc = None
    
    # Per-class metrics
    precision_pos = precision_score(y_test, test_pred, pos_label=1, zero_division=0)
    recall_pos = recall_score(y_test, test_pred, pos_label=1, zero_division=0)
    f1_pos = f1_score(y_test, test_pred, pos_label=1, zero_division=0)
    
    precision_neg = precision_score(y_test, test_pred, pos_label=0, zero_division=0)
    recall_neg = recall_score(y_test, test_pred, pos_label=0, zero_division=0)
    f1_neg = f1_score(y_test, test_pred, pos_label=0, zero_division=0)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, test_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    
    metrics = {
        "model_type": "logistic_regression",
        "accuracy": float(test_acc),
        "train_accuracy": float(train_acc),
        "baseline_accuracy": float(baseline_acc),
        "balanced_accuracy": float(test_bal_acc),
        "train_balanced_accuracy": float(train_bal_acc),
        "roc_auc": float(auc) if auc is not None else None,
        "precision_pos": float(precision_pos),
        "recall_pos": float(recall_pos),
        "f1_pos": float(f1_pos),
        "precision_neg": float(precision_neg),
        "recall_neg": float(recall_neg),
        "f1_neg": float(f1_neg),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        },
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "best_C": float(best_C) if best_C is not None else None,
        "decision_threshold": float(best_thr)
    }
    
    print(f"Train accuracy: {train_acc:.4f}")
    print(f"Test accuracy: {test_acc:.4f}")
    print(f"Train balanced accuracy: {train_bal_acc:.4f}")
    print(f"Test balanced accuracy: {test_bal_acc:.4f}")
    print(f"Baseline accuracy: {baseline_acc:.4f}")
    if auc is not None:
        print(f"Test ROC-AUC: {auc:.4f}")
    print(f"Precision (pos): {precision_pos:.4f}, Recall (pos): {recall_pos:.4f}")
    print(f"Precision (neg): {precision_neg:.4f}, Recall (neg): {recall_neg:.4f}")
    print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    
    return final_model, metrics


def train_random_forest(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    random_state: int = 42
) -> Tuple[RandomForestClassifier, Dict]:
    """
    Train regularized random forest model.
    
    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        random_state: Random seed
        
    Returns:
        (model, metrics_dict) tuple
    """
    print("\n" + "="*60)
    print("Training Random Forest (Regularized)")
    print("="*60)
    
    # Create model with strong regularization
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=4,  # Shallow trees to prevent overfitting
        min_samples_leaf=50,  # Require many samples per leaf
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1
    )
    
    # Train
    model.fit(X_train, y_train)
    
    # Predictions
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    test_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, test_pred)
    train_bal_acc = balanced_accuracy_score(y_train, train_pred)
    test_bal_acc = balanced_accuracy_score(y_test, test_pred)
    baseline_acc = compute_baseline_accuracy(y_test)
    
    try:
        auc = roc_auc_score(y_test, test_proba)
    except:
        auc = None
    
    # Per-class metrics
    precision_pos = precision_score(y_test, test_pred, pos_label=1, zero_division=0)
    recall_pos = recall_score(y_test, test_pred, pos_label=1, zero_division=0)
    f1_pos = f1_score(y_test, test_pred, pos_label=1, zero_division=0)
    
    precision_neg = precision_score(y_test, test_pred, pos_label=0, zero_division=0)
    recall_neg = recall_score(y_test, test_pred, pos_label=0, zero_division=0)
    f1_neg = f1_score(y_test, test_pred, pos_label=0, zero_division=0)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, test_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    
    metrics = {
        "model_type": "random_forest",
        "accuracy": float(test_acc),
        "train_accuracy": float(train_acc),
        "baseline_accuracy": float(baseline_acc),
        "balanced_accuracy": float(test_bal_acc),
        "train_balanced_accuracy": float(train_bal_acc),
        "roc_auc": float(auc) if auc is not None else None,
        "precision_pos": float(precision_pos),
        "recall_pos": float(recall_pos),
        "f1_pos": float(f1_pos),
        "precision_neg": float(precision_neg),
        "recall_neg": float(recall_neg),
        "f1_neg": float(f1_neg),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        },
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test))
    }
    
    print(f"Train accuracy: {train_acc:.4f}")
    print(f"Test accuracy: {test_acc:.4f}")
    print(f"Train balanced accuracy: {train_bal_acc:.4f}")
    print(f"Test balanced accuracy: {test_bal_acc:.4f}")
    print(f"Baseline accuracy: {baseline_acc:.4f}")
    if auc is not None:
        print(f"Test ROC-AUC: {auc:.4f}")
    print(f"Precision (pos): {precision_pos:.4f}, Recall (pos): {recall_pos:.4f}")
    print(f"Precision (neg): {precision_neg:.4f}, Recall (neg): {recall_neg:.4f}")
    print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    
    return model, metrics


# ============================================================================
# Main training function
# ============================================================================

def train_model(
    tickers: Optional[List[str]] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    test_size: float = DEFAULT_TEST_SIZE,
    label_threshold: float = DEFAULT_LABEL_THRESHOLD
):
    """
    Train ML models on historical data.
    
    Args:
        tickers: List of ticker symbols to use for training (default: all in DB)
        start_date: Start date for training data (default: 2020-01-01)
        end_date: End date for training data (default: today)
        test_size: Fraction of data to use for testing (default: 0.2)
        label_threshold: Threshold for positive label (default: 0.0)
    """
    # Handle incorrect system dates (if system date is in future)
    system_today = date.today()
    if system_today.year >= 2025:
        today = date(2024, 11, 20)
        print(f"[NOTE] System date appears incorrect ({system_today}), using {today} instead")
    else:
        today = system_today
    
    print("="*60)
    print("ML Model Training Pipeline")
    print("="*60)
    
    try:
        # Test database connection
        print("\nTesting database connection...")
        try:
            test_tickers = crud_supabase.get_tickers()
            print(f"✓ Database connection successful")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            print("\nPlease check your environment variables:")
            print("  - SUPABASE_URL")
            print("  - SUPABASE_KEY")
            return
        
        # Get tickers
        if tickers is None:
            all_tickers = crud_supabase.get_tickers()
            tickers = [t["symbol"] for t in all_tickers]
        
        if not tickers:
            print("No tickers found. Please add tickers to the database first.")
            return
        
        print(f"\nUsing tickers: {', '.join(tickers)}")
        
        # Auto-detect available date range from database
        print("\nDetecting available date range in database...")
        all_earliest_dates = []
        all_latest_dates = []
        
        for ticker_symbol in tickers:
            earliest = crud_supabase.get_earliest_price_date(ticker_symbol)
            latest = crud_supabase.get_latest_price_date(ticker_symbol)
            if earliest:
                all_earliest_dates.append(earliest)
            if latest:
                all_latest_dates.append(latest)
        
        if all_earliest_dates and all_latest_dates:
            detected_start = min(all_earliest_dates)
            detected_end = max(all_latest_dates)
            print(f"✓ Available date range: {detected_start} to {detected_end}")
            
            # Use detected range if dates not explicitly provided
            if start_date is None:
                start_date = detected_start
            if end_date is None:
                end_date = detected_end
            
            # If user provided dates but they don't match available data, use available data
            if start_date > detected_end or end_date < detected_start:
                print(f"⚠ Requested range ({start_date} to {end_date}) doesn't match available data")
                print(f"  Using available data range: {detected_start} to {detected_end}")
                start_date = detected_start
                end_date = detected_end
        else:
            # No data found, use defaults
            if start_date is None:
                start_date = DEFAULT_START_DATE
            if end_date is None:
                end_date = today
            print(f"⚠ No price data found in database. Will query range: {start_date} to {end_date}")
        
        print(f"\nQuerying data from {start_date} to {end_date}")
        print(f"Test size: {test_size:.1%}")
        print(f"Label threshold: {label_threshold}")
        
        # Collect features from all tickers
        all_features = []
        
        for ticker_symbol in tickers:
            print(f"\nProcessing {ticker_symbol}...")
            
            # Get prices with error handling and auto-adjust date range
            try:
                prices = crud_supabase.get_prices_sync(ticker_symbol, start_date, end_date)
            except Exception as e:
                print(f"  ✗ Error fetching prices: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            if not prices:
                # Check if there's any data at all for this ticker
                try:
                    earliest_date = crud_supabase.get_earliest_price_date(ticker_symbol)
                    latest_date = crud_supabase.get_latest_price_date(ticker_symbol)
                    if earliest_date and latest_date:
                        # Get all available data for this ticker
                        prices = crud_supabase.get_prices_sync(
                            ticker_symbol, 
                            earliest_date,
                            latest_date
                        )
                        if prices:
                            # Parse dates safely
                            def parse_date(d):
                                if isinstance(d, date):
                                    return d
                                elif isinstance(d, str):
                                    return date.fromisoformat(d.split('T')[0])  # Handle datetime strings
                                elif isinstance(d, datetime):
                                    return d.date()
                                else:
                                    return None
                            
                            price_dates = [parse_date(p["date"]) for p in prices if p.get("date")]
                            if price_dates:
                                actual_start_date = min(price_dates)
                                actual_end_date = max(price_dates)
                                print(f"  ✓ Found {len(prices)} price records (date range: {actual_start_date} to {actual_end_date})")
                            else:
                                print(f"  ✓ Found {len(prices)} price records")
                        else:
                            print(f"  ✗ No price data found in database for {ticker_symbol}")
                            continue
                    else:
                        print(f"  ✗ No price data found in database for {ticker_symbol}")
                        continue
                except Exception as e2:
                    print(f"  ✗ Error checking price data: {e2}")
                    import traceback
                    traceback.print_exc()
                    continue
            else:
                print(f"  ✓ Found {len(prices)} price records")
            
            # Get articles with error handling
            try:
                # Use the same date range as prices (or all available if we adjusted)
                if prices:
                    # Get the actual date range from prices
                    def parse_date(d):
                        if isinstance(d, date):
                            return d
                        elif isinstance(d, str):
                            return date.fromisoformat(d.split('T')[0])
                        elif isinstance(d, datetime):
                            return d.date()
                        else:
                            return None
                    
                    price_dates = [parse_date(p["date"]) for p in prices if p.get("date")]
                    if price_dates:
                        actual_start = min(price_dates)
                        actual_end = max(price_dates)
                        articles = crud_supabase.get_articles_sync(ticker_symbol, actual_start, actual_end)
                    else:
                        articles = crud_supabase.get_articles_sync(ticker_symbol, start_date, end_date)
                else:
                    articles = crud_supabase.get_articles_sync(ticker_symbol, start_date, end_date)
            except Exception as e:
                print(f"  ⚠ Error fetching articles: {e}")
                articles = []
            
            print(f"  ✓ Found {len(articles)} articles")
            
            # Compute features
            features_df = compute_features(prices, articles, label_threshold=label_threshold)
            if len(features_df) > 0:
                all_features.append(features_df)
        
        if not all_features:
            print("\n" + "="*60)
            print("ERROR: No features computed. Check data availability.")
            print("="*60)
            print("\nPossible issues:")
            print("1. Database has no price data - run data ingestion scripts")
            print("2. Date range doesn't match available data - check date ranges")
            print("3. Database connection issue - check SUPABASE_URL and SUPABASE_KEY")
            print("\nTo populate data, you can:")
            print("  - Use the /api/summary endpoint to trigger data fetching")
            print("  - Run scripts/backfill_news.py for news data")
            print("  - Run scripts/reset_and_backfill_prices.py for price data")
            return
        
        # Combine all features
        combined_features = pd.concat(all_features, ignore_index=True)
        print(f"\nTotal feature rows: {len(combined_features)}")
        
        # Sort by date for time-based split
        combined_features = combined_features.sort_values("date").reset_index(drop=True)
        
        # Time-based train/test split
        print(f"\nPerforming time-based train/test split...")
        train_df, test_df = time_based_train_test_split(
            combined_features,
            date_col="date",
            test_size=test_size
        )
        
        train_start_date = train_df["date"].min()
        train_end_date = train_df["date"].max()
        test_start_date = test_df["date"].min()
        test_end_date = test_df["date"].max()
        
        print(f"Train period: {train_start_date} to {train_end_date} ({len(train_df)} samples)")
        print(f"Test period: {test_start_date} to {test_end_date} ({len(test_df)} samples)")
        
        # Prepare training data
        X_train, y_train = prepare_training_data(train_df)
        X_test, y_test = prepare_training_data(test_df)
        
        print(f"\nFeature matrix shape: {X_train.shape} (train), {X_test.shape} (test)")
        
        # Class distribution
        train_dist = compute_class_distribution(y_train)
        test_dist = compute_class_distribution(y_test)
        baseline_acc = compute_baseline_accuracy(y_test)
        
        print(f"\nTrain class distribution: {train_dist}")
        print(f"Test class distribution: {test_dist}")
        print(f"Test baseline accuracy: {baseline_acc:.4f}")
        
        # Train models
        models_dir = Path(__file__).parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Train logistic regression
        log_reg_model, log_reg_metrics = train_logistic_regression(
            X_train, y_train, X_test, y_test
        )
        
        # Add common metadata
        log_reg_metrics.update({
            "class_distribution_train": train_dist,
            "class_distribution_test": test_dist,
            "train_start_date": train_start_date.isoformat(),
            "train_end_date": train_end_date.isoformat(),
            "test_start_date": test_start_date.isoformat(),
            "test_end_date": test_end_date.isoformat(),
            "n_tickers": len(tickers),
            "feature_names": get_feature_names(),
            "label_threshold": label_threshold
        })
        
        # Save logistic regression model
        log_reg_path = models_dir / "log_reg_model.pkl"
        with open(log_reg_path, "wb") as f:
            pickle.dump(log_reg_model, f)
        print(f"\nLogistic regression model saved to {log_reg_path}")
        
        # Save logistic regression metrics
        log_reg_metrics_path = models_dir / "log_reg_metrics.json"
        with open(log_reg_metrics_path, "w") as f:
            json.dump(log_reg_metrics, f, indent=2)
        print(f"Logistic regression metrics saved to {log_reg_metrics_path}")
        
        # Train random forest
        rf_model, rf_metrics = train_random_forest(
            X_train, y_train, X_test, y_test
        )
        
        # Add common metadata
        rf_metrics.update({
            "class_distribution_train": train_dist,
            "class_distribution_test": test_dist,
            "train_start_date": train_start_date.isoformat(),
            "train_end_date": train_end_date.isoformat(),
            "test_start_date": test_start_date.isoformat(),
            "test_end_date": test_end_date.isoformat(),
            "n_tickers": len(tickers),
            "feature_names": get_feature_names(),
            "label_threshold": label_threshold
        })
        
        # Save random forest model
        rf_path = models_dir / "rf_model.pkl"
        with open(rf_path, "wb") as f:
            pickle.dump(rf_model, f)
        print(f"\nRandom forest model saved to {rf_path}")
        
        # Save random forest metrics
        rf_metrics_path = models_dir / "rf_metrics.json"
        with open(rf_metrics_path, "w") as f:
            json.dump(rf_metrics, f, indent=2)
        print(f"Random forest metrics saved to {rf_metrics_path}")
        
        # Save primary model (use logistic regression as default)
        # This maintains backward compatibility
        primary_model_path = models_dir / "classifier.pkl"
        with open(primary_model_path, "wb") as f:
            pickle.dump(log_reg_model, f)
        
        primary_metrics_path = models_dir / "model_metrics.json"
        primary_metrics = {
            "accuracy": log_reg_metrics["accuracy"],
            "baseline_accuracy": log_reg_metrics["baseline_accuracy"],
            "auc": log_reg_metrics["roc_auc"],
            "balanced_accuracy": log_reg_metrics.get("balanced_accuracy"),
            "n_samples": log_reg_metrics["n_test"],  # Keep for backward compatibility
            "n_train": log_reg_metrics["n_train"],
            "n_test": log_reg_metrics["n_test"],
            "train_start_date": log_reg_metrics["train_start_date"],
            "train_end_date": log_reg_metrics["train_end_date"],
            "test_start_date": log_reg_metrics["test_start_date"],
            "test_end_date": log_reg_metrics["test_end_date"],
            "n_tickers": log_reg_metrics["n_tickers"],
            "feature_names": log_reg_metrics["feature_names"],
            "model_type": "logistic_regression",
            "best_C": log_reg_metrics.get("best_C"),
            "decision_threshold": log_reg_metrics.get("decision_threshold")
        }
        with open(primary_metrics_path, "w") as f:
            json.dump(primary_metrics, f, indent=2)
        
        print(f"\nPrimary model (logistic regression) saved to {primary_model_path}")
        print(f"Primary metrics saved to {primary_metrics_path}")
        
        print("\n" + "="*60)
        print("Training complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Default: train on all tickers with all available data
    train_model(
        tickers=DEFAULT_TICKERS,
        start_date=DEFAULT_START_DATE,
        end_date=DEFAULT_END_DATE,
        test_size=DEFAULT_TEST_SIZE,
        label_threshold=DEFAULT_LABEL_THRESHOLD
    )
