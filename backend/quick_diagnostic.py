"""
Quick diagnostic script to check backend health and identify issues.
Run this locally or in Render shell to diagnose problems.
"""
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[INFO] Loaded .env file from {env_path}")
    else:
        print(f"[INFO] No .env file found at {env_path}, using environment variables")
except ImportError:
    print("[INFO] python-dotenv not available, using environment variables only")

print("=" * 60)
print("Backend Diagnostic Script")
print("=" * 60)

# 1. Check environment variables
print("\n1. Checking environment variables...")
required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "ALPHAVANTAGE_API_KEY"]
optional_vars = ["OPENAI_API_KEY", "ALLOWED_ORIGINS"]
missing = []
for var in required_vars:
    if os.getenv(var):
        print(f"  ✓ {var} is set")
    else:
        print(f"  ✗ {var} is MISSING")
        missing.append(var)

for var in optional_vars:
    if os.getenv(var):
        print(f"  ✓ {var} is set (optional)")
    else:
        print(f"  - {var} is not set (optional)")

if missing:
    print(f"\n⚠️  Missing required environment variables: {', '.join(missing)}")
    sys.exit(1)

# 2. Check database connection
print("\n2. Testing database connection...")
try:
    from db import crud_supabase
    tickers = crud_supabase.get_tickers()
    print(f"  ✓ Database connection successful")
    print(f"  ✓ Found {len(tickers)} tickers in database")
    if tickers:
        print(f"  ✓ Sample tickers: {', '.join([t['symbol'] for t in tickers[:5]])}")
except Exception as e:
    print(f"  ✗ Database connection failed: {e}")
    sys.exit(1)

# 3. Check for price data
print("\n3. Checking price data availability...")
try:
    test_ticker = tickers[0]["symbol"] if tickers else "AAPL"
    latest_date = crud_supabase.get_latest_price_date(test_ticker)
    earliest_date = crud_supabase.get_earliest_price_date(test_ticker)
    
    if latest_date and earliest_date:
        print(f"  ✓ Price data exists for {test_ticker}")
        print(f"  ✓ Date range: {earliest_date} to {latest_date}")
        
        # Count prices
        prices = crud_supabase.get_prices(test_ticker, earliest_date, latest_date)
        print(f"  ✓ Found {len(prices)} price records")
    else:
        print(f"  ⚠️  No price data found for {test_ticker}")
except Exception as e:
    print(f"  ✗ Error checking price data: {e}")

# 4. Check for news articles
print("\n4. Checking news articles...")
try:
    test_ticker = tickers[0]["symbol"] if tickers else "AAPL"
    today = date.today()
    start_date = today - timedelta(days=30)
    
    articles = crud_supabase.get_articles(test_ticker, start_date, today, relevant_only=True)
    print(f"  ✓ Found {len(articles)} articles for {test_ticker} (last 30 days)")
    
    if articles:
        articles_with_sentiment = [a for a in articles if a.get("sentiment_score") is not None]
        print(f"  ✓ {len(articles_with_sentiment)} articles have sentiment scores")
        
        # Count sentiment distribution
        negative = sum(1 for a in articles_with_sentiment if a.get("sentiment_score", 0) < -0.1)
        neutral = sum(1 for a in articles_with_sentiment if -0.1 <= a.get("sentiment_score", 0) <= 0.1)
        positive = sum(1 for a in articles_with_sentiment if a.get("sentiment_score", 0) > 0.1)
        print(f"  ✓ Sentiment distribution: {negative} negative, {neutral} neutral, {positive} positive")
except Exception as e:
    print(f"  ✗ Error checking articles: {e}")

# 5. Check model files
print("\n5. Checking model files...")
models_dir = Path(__file__).parent / "models"
if models_dir.exists():
    model_files = list(models_dir.glob("*.pkl"))
    metrics_files = list(models_dir.glob("*_metrics.json"))
    
    print(f"  ✓ Models directory exists")
    print(f"  ✓ Found {len(model_files)} model files")
    print(f"  ✓ Found {len(metrics_files)} metrics files")
    
    if model_files:
        for f in model_files:
            size_kb = f.stat().st_size / 1024
            print(f"    - {f.name} ({size_kb:.1f} KB)")
    else:
        print(f"  ⚠️  No model files found. Run 'python train_model.py' to train models.")
    
    if metrics_files:
        for f in metrics_files:
            print(f"    - {f.name}")
    else:
        print(f"  ⚠️  No metrics files found.")
else:
    print(f"  ✗ Models directory does not exist")

# 6. Test API imports
print("\n6. Testing API imports...")
try:
    from services.data_refresh import ensure_price_data, ensure_news_data
    from services.model_inference import get_model_inference
    print(f"  ✓ All service imports successful")
except Exception as e:
    print(f"  ✗ Import error: {e}")
    import traceback
    traceback.print_exc()

# 7. Test model inference
print("\n7. Testing model inference...")
try:
    model_inference = get_model_inference()
    if model_inference.model is not None:
        print(f"  ✓ Model loaded successfully")
        metrics = model_inference.get_metrics()
        if metrics:
            print(f"  ✓ Model metrics available")
            print(f"    - Accuracy: {metrics.get('accuracy', 'N/A')}")
            print(f"    - Baseline: {metrics.get('baseline_accuracy', 'N/A')}")
        else:
            print(f"  ⚠️  Model loaded but no metrics available")
    else:
        print(f"  ⚠️  Model is None - may need to train model first")
except Exception as e:
    print(f"  ✗ Model inference error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic complete!")
print("=" * 60)
print("\nIf you see any ✗ errors above, those need to be fixed.")
print("Share the output of this script along with your logs for debugging.")

