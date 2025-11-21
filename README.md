# News & Sentiment Driven Stock Explorer

A full-stack machine learning web application that analyzes the relationship between news sentiment and stock price movements. Built as a portfolio-quality project demonstrating end-to-end ML and data science capabilities.

## 🎯 Project Overview

This application allows users to:
- Select a stock ticker and date range
- View price charts with overlayed sentiment data
- Browse news articles with AI-generated sentiment scores
- See ML-based insights predicting short-term returns based on sentiment

### Key Features

- **Live Data Integration**: Fetches real-time data from Yahoo Finance (prices) and Alpha Vantage (news)
- **Smart Caching**: Uses Supabase Postgres to cache data and reduce API calls
- **AI-Powered Sentiment**: Uses Alpha Vantage's built-in sentiment analysis (OpenAI optional for enrichment)
- **ML Predictions**: RandomForest model predicts 3-day return probabilities
- **Modern UI**: Clean, responsive React frontend with interactive charts

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   Backend   │────────▶│  Supabase   │
│  (React)    │         │  (FastAPI)   │         │  Postgres   │
│   Vercel    │         │    Render    │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ├──▶ Yahoo Finance (Prices - via yfinance)
                               ├──▶ Alpha Vantage (News & Sentiment)
                               └──▶ OpenAI API (Optional sentiment enrichment)
```

### Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (web framework)
- Supabase Postgres (database via Supabase client)
- scikit-learn (ML model)
- Alpha Vantage API (news & sentiment)
- OpenAI API (optional sentiment enrichment)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- Recharts (data visualization)

**External APIs:**
- Yahoo Finance (stock price data via yfinance library - free, no API key)
- Alpha Vantage (news headlines & built-in sentiment analysis)
- OpenAI (optional sentiment enrichment)

## 📁 Project Structure

```
news-stock-sentiment-explorer/
├── backend/
│   ├── app.py                      # FastAPI entrypoint
│   ├── train_model.py              # ML model training script
│   ├── init_db.py                  # Database initialization
│   ├── ingest/
│   │   ├── yfinance_client.py     # Yahoo Finance price data client
│   │   ├── alphavantage_news_client.py  # Alpha Vantage news client
│   │   └── openai_sentiment.py    # OpenAI sentiment analysis (optional)
│   ├── db/
│   │   ├── models.py              # Database models
│   │   ├── crud_supabase.py       # Database operations
│   │   └── supabase_client.py    # Supabase client setup
│   ├── services/
│   │   ├── data_refresh.py        # Cache refresh logic
│   │   ├── feature_engineering.py # ML feature computation
│   │   └── model_inference.py     # Model prediction service
│   ├── schemas/
│   │   └── models.py              # Pydantic schemas
│   ├── models/
│   │   ├── classifier.pkl         # Trained ML model
│   │   └── model_metrics.json     # Model performance metrics
│   ├── requirements.txt
│   └── README_BACKEND.md
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── api/
│   │   │   └── client.ts          # API client
│   │   ├── types/                 # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── README_FRONTEND.md
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account (free tier works)
- API keys:
  - Alpha Vantage: https://www.alphavantage.co/support/#api-key (free tier available)
  - OpenAI: https://platform.openai.com (optional - Alpha Vantage provides sentiment)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the `backend/` directory (see `backend/ENV_TEMPLATE.md` for details):
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
ALPHAVANTAGE_API_KEY=your_alphavantage_key
OPENAI_API_KEY=your_openai_key  # Optional
```

5. **Initialize database:**
```bash
python init_db.py
```
This creates the tables and seeds initial tickers (AAPL, MSFT, etc.).

6. **Train the ML model:**
```bash
python train_model.py
```
This will:
- Load historical data from the database
- Compute features (sentiment, returns, volatility)
- Train a RandomForest classifier
- Save the model to `models/classifier.pkl`
- Save metrics to `models/model_metrics.json`

7. **Start the API server:**
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
Create a `.env.local` file in the `frontend/` directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```

4. **Start development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📊 How It Works

### Data Flow

1. **User Request**: User selects ticker and date range, clicks "Analyze"
2. **Cache Check**: Backend checks Supabase for existing price/news data
3. **API Fetch**: If data is missing or stale, fetches from Yahoo Finance (prices) and Alpha Vantage (news)
4. **Sentiment Analysis**: Alpha Vantage provides built-in sentiment scores; OpenAI can optionally enrich
5. **Caching**: All data is stored in Supabase for future requests
6. **Feature Engineering**: ML features are computed (sentiment averages, returns, volatility)
7. **Model Inference**: Trained model predicts probability of positive 3-day returns
8. **Response**: Frontend displays prices, sentiment, articles, and insights

### ML Model

**Target Variable:**
- `future_3d_return_positive`: Binary (1 if cumulative return over next 3 trading days > 0, else 0)

**Features:**
- `sentiment_avg`: Daily average sentiment score (-1 to 1)
- `sentiment_rolling_mean_3d`: 3-day rolling mean of sentiment
- `return_1d`: 1-day return (percentage change)
- `volatility_5d`: 5-day rolling standard deviation of returns

**Model:**
- RandomForestClassifier (100 trees, max depth 10)
- Trained on historical data from multiple tickers
- Evaluated with accuracy, baseline accuracy, and ROC-AUC

**Insights:**
The model provides probabilities of positive 3-day returns, which are compared to baseline rates to generate insights about sentiment's predictive power.

### Data Quality & Relevance Filtering

**Problem:**
Initially, the database contained many generic business news articles that weren't specific to the tracked tickers. Examples included:
- Market research reports ("Astrocytoma Market Research and Forecast Report 2025–2035...")
- Law firm investor alerts ("INVESTOR ALERT: Pomerantz Law Firm...")
- Generic industry analysis ("The Biotech Sector is Seeing a Major Boost...")
- Political/geopolitical news unrelated to specific companies

This noise reduced the explanatory power of sentiment features and degraded ML model performance.

**Solution:**
We implemented a two-level relevance filtering system:

1. **Ticker-Focused Queries**: NewsAPI queries are built using ticker-specific search terms (company name, ticker symbol, product names) combined with finance keywords. This ensures we fetch articles that are likely about the specific ticker.

2. **Post-Fetch Relevance Filtering**:
   - **Positive Match**: Articles must contain company/ticker-specific terms (e.g., "Apple", "AAPL", "iPhone" for AAPL)
   - **Negative Filter**: Articles containing noise phrases are filtered out:
     - Market research reports ("market research report", "forecast report 2025-2035")
     - Law firm spam ("investor alert", "class action lawsuit", "fraud investigation")
     - Generic rankings ("Deloitte Technology Fast 500", "fastest-growing company")
     - Political/geopolitical news unrelated to the company

3. **Database Tracking**: The `news_articles` table includes an `is_relevant` boolean column. Only articles with `is_relevant = true` are used for:
   - Sentiment feature engineering
   - ML model training
   - API responses to the frontend

**Configuration:**
- Ticker search terms are defined in `backend/config/news_queries.py`
- Noise phrases are defined in `backend/config/relevance_filter.py`
- Both can be easily extended for new tickers or additional filtering rules

**Future Extensibility:**
The code is structured to allow adding macro "US market sentiment" as a separate pipeline and feature set without changing the ticker-specific logic.

### Caching Strategy

The app uses a "live-ish" approach:
- **Price Data**: Cached in `daily_prices` table. Fetched from Yahoo Finance if missing or stale (>1 day old)
- **News Data**: Cached in `news_articles` table. 
  - **API endpoint** (`/api/summary`): Only fetches if missing AND very recent (last 2 days)
  - **Large backfills**: Use dedicated script `backend/scripts/backfill_news.py` (see below)
- **Sentiment**: Provided by Alpha Vantage and cached. OpenAI can optionally enrich new articles

This reduces API calls while keeping data reasonably fresh.

### News Backfill (Ticker-Relevant Only)

For repopulating the database with ticker-relevant news, use the dedicated backfill script:

**Dry-run (preview without API calls):**
```bash
cd backend
python -m scripts.backfill_news --tickers AAPL,MSFT,TSLA --start-date 2024-06-01 --end-date 2024-09-01 --dry-run
```

**Actual backfill:**
```bash
python -m scripts.backfill_news --tickers AAPL,MSFT,TSLA --start-date 2024-06-01 --end-date 2024-09-01 --no-dry-run
```

**Features:**
- ✅ Dry-run mode by default (zero API calls)
- ✅ Only fetches ticker-focused, relevance-filtered news
- ✅ Deduplicates by checking existing data
- ✅ Respects Alpha Vantage rate limits with throttling
- ✅ Never runs automatically - must be explicitly invoked

See `backend/README_BACKEND.md` for more details.

## 🗄️ Database Schema

### Tables

**tickers**
- `id` (PK)
- `symbol` (unique, e.g., 'AAPL')
- `name` (optional company name)

**daily_prices**
- `id` (PK)
- `ticker_symbol` (FK)
- `date`
- `open`, `high`, `low`, `close`
- `volume`
- Unique constraint on (ticker_symbol, date)

**news_articles**
- `id` (PK)
- `ticker_symbol` (FK)
- `published_at`
- `headline`
- `source`
- `url`
- `sentiment_score` (nullable, -1 to 1)
- `sentiment_label` (nullable: 'Positive', 'Neutral', 'Negative')
- `raw_text` (optional)
- `is_relevant` (boolean, default true) - Indicates if article is relevant to the ticker

**daily_features** (optional, for ML)
- `id` (PK)
- `ticker_symbol`, `date`
- `sentiment_avg`, `sentiment_rolling_mean_3d`
- `return_1d`, `volatility_5d`
- `future_3d_return_positive` (target)

## 🌐 Deployment

**🚀 New to deploying? Start with [`DEPLOYMENT_STEPS.md`](DEPLOYMENT_STEPS.md) for complete step-by-step instructions!**

This project is configured for production deployment on:
- **Backend**: Render (FastAPI web service)
- **Frontend**: Vercel (React + Vite static site)
- **Database**: Supabase Postgres (external)

**Quick Links:**
- 📖 **[Complete Deployment Guide](DEPLOYMENT_STEPS.md)** - Step-by-step instructions with all accounts to create
- ✅ **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)** - Quick checklist to track your progress

### Prerequisites

Before deploying, ensure you have:
1. A Supabase account and project (free tier works)
2. API keys:
   - Alpha Vantage API key (required for news data)
   - OpenAI API key (optional, for sentiment enrichment)
3. GitHub repository with your code pushed

### Backend Deployment on Render

#### Step 1: Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: Choose a name (e.g., `news-stock-backend`)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free tier works for testing, upgrade for production

#### Step 2: Set Environment Variables

In Render dashboard, go to your service → **Environment** tab and add:

**Required:**
- `SUPABASE_URL`: Your Supabase project URL (from Supabase dashboard → Settings → API)
- `SUPABASE_KEY`: Your Supabase anon/public key (from Supabase dashboard → Settings → API)
- `ALPHAVANTAGE_API_KEY`: Your Alpha Vantage API key (get from https://www.alphavantage.co/support/#api-key)

**Optional:**
- `OPENAI_API_KEY`: Your OpenAI API key (optional, for sentiment enrichment)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (e.g., `https://your-frontend.vercel.app`)
  - If not set, defaults to: `http://localhost:5173,http://localhost:3000,https://*.vercel.app`

**Note:** `PORT` is automatically set by Render - don't set it manually.

#### Step 3: Initialize Database

After the first deployment:

1. **SSH into your Render instance** (via Render dashboard → Shell)
2. **Create tables** by running the SQL script in Supabase:
   - Go to Supabase dashboard → SQL Editor
   - Run the contents of `backend/db/init_supabase_tables.sql`
   - Run any migration scripts in `backend/db/` (e.g., `migrate_add_is_relevant.sql`)
3. **Seed tickers**: From Render shell, run:
   ```bash
   python init_db.py
   ```
4. **Train the ML model**:
   ```bash
   python train_model.py
   ```

Alternatively, you can run these commands locally before deployment (they connect to your Supabase database via environment variables).

#### Step 4: Verify Deployment

- Check the service logs in Render dashboard
- Test the health endpoint: `https://your-service.onrender.com/health` (should return `{"status": "ok"}`)
- Test the root endpoint: `https://your-service.onrender.com/` (should return API message)
- Render will automatically configure health checks using the `/health` endpoint

#### Step 5: Get Your Backend URL

After deployment, note your backend URL (e.g., `https://your-service.onrender.com`). You'll need this for the frontend configuration.

---

### Frontend Deployment on Vercel

#### Step 1: Create Project on Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)

#### Step 2: Set Environment Variables

In Vercel project settings → **Environment Variables**, add:

**Required:**
- `VITE_API_BASE_URL`: Your Render backend URL (e.g., `https://your-service.onrender.com`)
  - **Important**: For production, include the protocol (`https://`)
  - This is used by the frontend to make API calls

#### Step 3: Deploy

1. Click **"Deploy"**
2. Wait for build to complete
3. Vercel will provide you with a deployment URL (e.g., `https://your-project.vercel.app`)

#### Step 4: Update Backend CORS (if needed)

If you want to restrict CORS to only your Vercel domain:

1. Go to Render dashboard → Your backend service → Environment
2. Add/update `ALLOWED_ORIGINS`:
   ```
   https://your-project.vercel.app
   ```
   (Replace with your actual Vercel domain)

Alternatively, leave it unset to use defaults which include `https://*.vercel.app` (wildcard for all Vercel deployments).

#### Step 5: Test the Integration

1. Open your Vercel deployment URL
2. Try selecting a ticker and date range
3. Verify API calls work (check browser DevTools → Network tab)
4. Verify data loads correctly

---

### Supabase Setup

1. **Create a new project** on [Supabase](https://supabase.com)
2. **Get your credentials**:
   - Go to Settings → API
   - Copy `Project URL` → use as `SUPABASE_URL`
   - Copy `anon` `public` key → use as `SUPABASE_KEY`
3. **Create database tables**:
   - Go to SQL Editor in Supabase dashboard
   - Run the SQL from `backend/db/init_supabase_tables.sql`
   - Run any migration scripts in `backend/db/` (e.g., `migrate_add_is_relevant.sql`)
4. **Configure Row Level Security (RLS)**:
   - For development, you can disable RLS on tables
   - For production, configure RLS policies as needed
5. **Set environment variables** in Render with your Supabase credentials

---

### Local Development Setup

For local development before deployment:

#### Backend

1. **Create `.env` file** in `backend/` directory (copy from `backend/.env.example`):
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key
   ALPHAVANTAGE_API_KEY=your-alpha-vantage-key
   OPENAI_API_KEY=your-openai-key  # Optional
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Initialize database** (if not done in Supabase SQL Editor):
   ```bash
   python init_db.py
   ```

4. **Train model**:
   ```bash
   python train_model.py
   ```

5. **Start server**:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

#### Frontend

1. **Create `.env.local` file** in `frontend/` directory (copy from `frontend/.env.example`):
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

2. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

---

### Environment Variables Summary

#### Backend (Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon/public key |
| `ALPHAVANTAGE_API_KEY` | Yes | Alpha Vantage API key for news |
| `OPENAI_API_KEY` | No | OpenAI API key (optional) |
| `ALLOWED_ORIGINS` | No | Comma-separated CORS origins |
| `PORT` | Auto | Set automatically by Render |

#### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes | Backend API URL (e.g., `https://your-backend.onrender.com`) |

---

### Deployment Checklist

- [ ] Supabase project created and tables initialized
- [ ] Backend deployed on Render with all environment variables set
- [ ] Backend health check works (`/health` endpoint)
- [ ] Database seeded with tickers (`python init_db.py`)
- [ ] ML model trained (`python train_model.py`)
- [ ] Frontend deployed on Vercel with `VITE_API_BASE_URL` set
- [ ] CORS configured correctly (backend allows frontend origin)
- [ ] End-to-end testing: frontend can fetch data from backend
- [ ] All API keys are set in deployment environment (not committed to git)

## 📝 API Endpoints

### `GET /health` or `GET /healthz`
Health check endpoint for deployment platforms (e.g., Render). Returns a simple status response.

**Response:**
```json
{
  "status": "ok"
}
```

### `GET /api/tickers`
Returns list of available tickers.

**Response:**
```json
[
  { "symbol": "AAPL", "name": "Apple Inc." },
  ...
]
```

### `GET /api/summary?ticker=AAPL&start_date=2024-01-01&end_date=2024-03-31`
Returns comprehensive analysis for a ticker and date range.

**Response:**
```json
{
  "ticker": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "n_articles": 42,
  "avg_sentiment": 0.23,
  "price_series": [
    { "date": "2024-01-01", "close": 189.12 },
    ...
  ],
  "sentiment_series": [
    { "date": "2024-01-01", "sentiment_avg": 0.15 },
    ...
  ],
  "articles": [
    {
      "date": "2024-01-01",
      "headline": "...",
      "source": "...",
      "url": "...",
      "sentiment_score": 0.7,
      "sentiment_label": "Positive"
    }
  ],
  "model_insights": {
    "mean_positive_prob": 0.61,
    "baseline_positive_rate": 0.52,
    "comment": "..."
  }
}
```

### `GET /api/model-metrics`
Returns ML model training metrics.

**Response:**
```json
{
  "accuracy": 0.65,
  "baseline_accuracy": 0.52,
  "auc": 0.68,
  "n_samples": 1234,
  "train_start_date": "2023-01-01",
  "train_end_date": "2024-01-01",
  "n_tickers": 10,
  "feature_names": ["sentiment_avg", "sentiment_rolling_mean_3d", "return_1d", "volatility_5d"]
}
```

## 🧪 Development Notes

### Adding New Tickers

Add tickers to the database:
```python
from db.session import SessionLocal
from db.models import Ticker

db = SessionLocal()
ticker = Ticker(symbol="TSLA", name="Tesla Inc.")
db.add(ticker)
db.commit()
```

Or use the `init_db.py` script and modify the tickers list.

### Retraining the Model

Simply run:
```bash
python train_model.py
```

The script will:
- Load all available data from the database
- Retrain the model
- Save updated model and metrics

### Testing API Locally

```bash
# Start backend
cd backend
uvicorn app:app --reload

# In another terminal, test endpoints
curl http://localhost:8000/api/tickers
curl "http://localhost:8000/api/summary?ticker=AAPL&start_date=2024-01-01&end_date=2024-03-31"
```

## 🐛 Troubleshooting

**Database connection errors:**
- Verify `DATABASE_URL` is correct
- Check Supabase project is active
- Ensure IP is whitelisted (if required)

**API rate limits:**
- Yahoo Finance (yfinance): Free, no rate limits (but be respectful)
- Alpha Vantage free tier: 5 calls/minute, 500 calls/day
- OpenAI: Pay-per-use

**Model not found:**
- Run `python train_model.py` to train the model
- Ensure `models/classifier.pkl` exists

**Frontend can't connect to backend:**
- Check `VITE_API_BASE_URL` is set correctly
- Verify backend is running
- Check CORS settings in `app.py`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Supabase Documentation](https://supabase.com/docs)
- [Finnhub API Docs](https://finnhub.io/docs/api)
- [NewsAPI Documentation](https://newsapi.org/docs)

## 📄 License

This project is open source and available for portfolio use.

## 🙏 Acknowledgments

- Built as a portfolio project to demonstrate full-stack ML capabilities
- Uses free tiers of external APIs where possible
- Designed for easy deployment and demonstration

---

**Note**: This is a portfolio project. For production use, consider:
- More robust error handling
- Rate limiting
- Authentication/authorization
- More sophisticated ML models
- Real-time data streaming
- Background job processing for data ingestion

