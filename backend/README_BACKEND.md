# Backend Documentation

## Overview

FastAPI backend for the News & Sentiment Driven Stock Explorer. Handles data ingestion, caching, ML model inference, and API endpoints.

## Architecture

- **FastAPI**: Web framework
- **Supabase Postgres**: Database (via Supabase Python client)
- **External APIs**: Yahoo Finance (prices via yfinance), Alpha Vantage (news & sentiment), OpenAI (optional sentiment enrichment)
- **ML Model**: RandomForestClassifier for predicting positive 3-day returns

## Setup

1. Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Set up environment variables (see `ENV_TEMPLATE.md` for template):
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key
- `ALPHAVANTAGE_API_KEY`: From https://www.alphavantage.co/support/#api-key (for news)
- `OPENAI_API_KEY`: From https://platform.openai.com (optional - Alpha Vantage provides sentiment)

3. Initialize database:
```bash
python init_db.py
```

4. Train model:
```bash
python train_model.py
```

   This will:
   - Load all available data from Supabase
   - Compute features and labels (3-day forward returns)
   - Split data chronologically (time-based split)
   - Train logistic regression and random forest models
   - Save models and metrics to `models/` directory
   
   **Note**: Training uses only database data - no external API calls during training.

5. Start API:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Data Flow

1. **Request comes in** → `/api/summary?ticker=AAPL&start_date=...&end_date=...`
2. **Check cache** → Query Supabase for existing price/news data
3. **Fetch if needed** → Call Yahoo Finance (prices) / Alpha Vantage (news) if data is missing/stale
4. **Sentiment analysis** → Alpha Vantage provides built-in sentiment; OpenAI can optionally enrich
5. **Cache results** → Store in Supabase
6. **Compute features** → Generate ML features
7. **Model inference** → Predict probabilities using trained model
8. **Return response** → JSON with prices, sentiment, articles, insights

## API Endpoints

- `GET /api/tickers` - List available tickers
- `GET /api/summary` - Get analysis for ticker and date range
- `GET /api/model-metrics` - Get model training metrics

## Model

The ML model predicts whether a stock will have a positive return over the next 3 trading days based on:
- Daily average sentiment (weighted by relevance score)
- 3-day rolling mean of sentiment
- 1-day return
- 5-day volatility

### Model Training

The training pipeline implements best practices for time-series ML:

1. **Time-based train/test split**: Data is split chronologically (not randomly) to avoid data leakage
   - Train: earliest 70-80% of dates
   - Test: latest 20-30% of dates

2. **No data leakage**: Features only use data up to and including date `t`, labels are based on returns from `t+1` to `t+3`

3. **Multiple models trained**:
   - **Logistic Regression** (regularized baseline): Strong regularization (C=0.1), balanced class weights
   - **Random Forest** (regularized): Shallow trees (max_depth=4), high min_samples_leaf (50) to prevent overfitting

4. **Comprehensive metrics**: Each model reports:
   - Accuracy (train and test)
   - Baseline accuracy (majority class frequency)
   - ROC-AUC
   - Precision, recall, F1 for each class
   - Confusion matrix
   - Class distribution

### Training Script

Training script: `train_model.py`

**Usage:**
```bash
cd backend
python train_model.py
```

**Configuration** (at top of `train_model.py`):
- `DEFAULT_TICKERS`: List of tickers or `None` for all tickers
- `DEFAULT_START_DATE`: Start date for data (default: 2020-01-01)
- `DEFAULT_END_DATE`: End date (default: today)
- `DEFAULT_TEST_SIZE`: Fraction for test set (default: 0.2)
- `DEFAULT_LABEL_THRESHOLD`: Threshold for positive label (default: 0.0)

**Output:**
- `models/log_reg_model.pkl` - Logistic regression model
- `models/log_reg_metrics.json` - Logistic regression metrics
- `models/rf_model.pkl` - Random forest model
- `models/rf_metrics.json` - Random forest metrics
- `models/classifier.pkl` - Primary model (logistic regression by default, for backward compatibility)
- `models/model_metrics.json` - Primary metrics (for backward compatibility)

### Model Evaluation

The training script provides honest, interpretable metrics:
- **Test accuracy vs baseline**: Shows if the model beats a simple majority-class baseline
- **ROC-AUC**: Measures discrimination ability (0.5 = random, 1.0 = perfect)
- **Train vs test accuracy gap**: Indicates overfitting (large gap = overfitting)
- **Class distribution**: Shows data balance

**Note**: If test accuracy ≈ baseline accuracy or ROC-AUC < 0.5, the model has no predictive power. This is expected for financial prediction tasks where signals are weak.

## News Relevance Filtering

To ensure data quality, the system implements ticker-specific news filtering:

### Configuration

- **Ticker Search Terms**: Defined in `config/news_queries.py`
  - Each ticker has company-specific search terms (e.g., "Apple", "AAPL", "iPhone" for AAPL)
  - Used for relevance filtering and scoring

- **Noise Filtering**: Defined in `config/relevance_filter.py`
  - Filters out market research reports, law firm spam, generic rankings, etc.
  - Uses both positive matching (must mention company) and negative filtering (must not contain noise phrases)

### Database Schema

The `news_articles` table includes an `is_relevant` boolean column:
- `is_relevant = true`: Article is relevant to the ticker and used for sentiment/ML
- `is_relevant = false`: Article is noise and excluded from analysis

### Migration

If upgrading an existing database, run:
```sql
-- See backend/db/migrate_add_is_relevant.sql
ALTER TABLE news_articles ADD COLUMN is_relevant BOOLEAN DEFAULT true;
CREATE INDEX idx_news_articles_relevant ON news_articles(is_relevant) WHERE is_relevant = true;
```

### Testing

Test relevance filtering:
```bash
python test_relevance_filtering.py
```

Validate news quality for a ticker:
```bash
python validate_news_quality.py AAPL 7  # symbol and days_back
```

## News Backfill (Ticker-Relevant Only)

For repopulating the `news_articles` database with ticker-relevant news, use the dedicated backfill script.

### Important Notes

- **Never runs automatically** - must be explicitly invoked
- **Dry-run mode by default** - previews what would be fetched without making API calls
- **Only fetches ticker-focused, relevance-filtered news** - uses the same filtering as normal ingestion
- **Respects rate limits** - includes throttling between requests

### Usage

#### 1. Dry-Run (Preview)

Preview what would be fetched without making any API calls:

```bash
cd backend
python -m scripts.backfill_news --tickers AAPL,MSFT,TSLA --start-date 2024-06-01 --end-date 2024-09-01 --dry-run
```

This will show:
- Which tickers will be processed
- Missing date ranges that need fetching
- Estimated number of API calls

#### 2. Actual Backfill

After reviewing the dry-run output, run with `--no-dry-run`:

```bash
python -m scripts.backfill_news --tickers AAPL,MSFT,TSLA --start-date 2024-06-01 --end-date 2024-09-01 --no-dry-run
```

**Important**: Make sure `ALPHAVANTAGE_API_KEY` is set in your `.env` file before running actual backfill.

### How It Works

1. **Checks existing data**: Identifies which date ranges already have articles
2. **Finds gaps**: Only fetches missing date ranges (chunked by week)
3. **Ticker-focused queries**: Uses the same ticker-specific query building as normal ingestion
4. **Relevance filtering**: Applies `is_article_relevant_to_ticker()` to each article
5. **Deduplication**: Uses database uniqueness constraints to avoid duplicates
6. **Rate limiting**: Includes 1-second delay between requests

### API Endpoint Behavior

The `/api/summary` endpoint uses `ensure_news_data()`, which is **conservative**:
- Only fetches if data is completely missing
- Only fetches for very recent dates (last 2 days by default)
- For older date ranges, relies on existing database data

**For large backfills, always use the dedicated script, not the API endpoint.**

