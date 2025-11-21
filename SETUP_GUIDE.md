# 🚀 Complete Setup Guide for News-Sentiment-Driven-Stock-Explorer

This guide will walk you through everything you need to get the application running.

## 📋 Overview

You need to set up:
1. **Supabase** (PostgreSQL database) - FREE tier available
2. **Finnhub API** (Stock price data) - FREE tier available
3. **NewsAPI.org** (News articles) - FREE tier available
4. **OpenAI API** (Sentiment analysis) - Pay-per-use (very affordable)

---

## 🔑 Step 1: Get API Keys

### 1.1 Supabase (Database)

**What it is:** PostgreSQL database hosted in the cloud

**Steps:**
1. Go to https://supabase.com
2. Click **"Start your project"** or **"Sign up"**
3. Sign up with GitHub, Google, or email
4. Click **"New Project"**
5. Fill in:
   - **Name**: `news-stock-explorer` (or any name)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you
   - **Pricing Plan**: Free tier is fine
6. Click **"Create new project"**
7. Wait 2-3 minutes for project to initialize

**Get Connection String:**
1. Once project is ready, go to **Settings** (gear icon) → **Database**
2. Scroll down to **"Connection string"**
3. Under **"Connection pooling"**, copy the **"URI"** connection string
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`
   - Replace `[YOUR-PASSWORD]` with the password you created
4. **Save this connection string** - you'll need it for `DATABASE_URL`

---

### 1.2 Finnhub API (Stock Prices)

**What it is:** Provides stock price data

**Steps:**
1. Go to https://finnhub.io
2. Click **"Get Free API Key"** or **"Sign Up"**
3. Sign up with email or GitHub
4. Verify your email if required
5. Once logged in, you'll see your **API Key** on the dashboard
6. **Copy and save this key**

**Free Tier Limits:**
- 60 API calls per minute
- Sufficient for development and testing

---

### 1.3 NewsAPI.org (News Articles)

**What it is:** Provides news articles and headlines

**Steps:**
1. Go to https://newsapi.org
2. Click **"Get API Key"** or **"Sign Up"**
3. Sign up with email
4. Verify your email
5. Once logged in, go to **"API Keys"** section
6. Your API key will be displayed
7. **Copy and save this key**

**Free Tier Limits:**
- 100 requests per day
- Development tier (for testing only)
- For production, consider upgrading

---

### 1.4 OpenAI API (Sentiment Analysis)

**What it is:** AI service for analyzing news sentiment

**Steps:**
1. Go to https://platform.openai.com
2. Click **"Sign up"** or **"Log in"**
3. Create an account (or sign in)
4. Go to **"API Keys"** section (left sidebar)
5. Click **"Create new secret key"**
6. Give it a name (e.g., "News Sentiment App")
7. **Copy the key immediately** - you won't see it again!
8. **Save this key securely**

**Pricing:**
- Pay-per-use (very affordable for small projects)
- GPT-3.5-turbo costs ~$0.001-0.002 per article analyzed
- You can set usage limits in OpenAI dashboard

---

## 📝 Step 2: Configure Environment Variables

### 2.1 Backend Configuration

1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. Create a `.env` file in the `backend` folder:
   - On Windows: Create a new file named `.env` (make sure it's not `.env.txt`)
   - You can use Notepad, VS Code, or any text editor

3. Add the following content to `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
   FINNHUB_API_KEY=your_finnhub_api_key_here
   NEWSAPI_API_KEY=your_newsapi_key_here
   OPENAI_API_KEY=sk-your_openai_key_here
   ```

4. **Replace the values:**
   - `DATABASE_URL`: Paste your Supabase connection string (replace `YOUR_PASSWORD` with your actual password)
   - `FINNHUB_API_KEY`: Your Finnhub API key
   - `NEWSAPI_API_KEY`: Your NewsAPI key
   - `OPENAI_API_KEY`: Your OpenAI API key (starts with `sk-`)

**Example `.env` file:**
```env
DATABASE_URL=postgresql://postgres:MySecurePass123@db.abcdefgh.supabase.co:5432/postgres
FINNHUB_API_KEY=abc123def456ghi789
NEWSAPI_API_KEY=xyz789uvw456rst123
OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz1234567890
```

**⚠️ Important:**
- Never commit the `.env` file to Git (it should already be in `.gitignore`)
- Keep your API keys secret
- The `.env` file should be in the `backend/` folder, not the root folder

---

### 2.2 Frontend Configuration

1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```

2. Create a `.env.local` file in the `frontend` folder

3. Add the following content:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

**For Production:**
If you deploy the backend to a service like Render, update this to:
```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

---

## 🗄️ Step 3: Initialize Database

1. Make sure you're in the `backend` folder
2. Activate your Python virtual environment (if you have one):
   ```bash
   # On Windows PowerShell:
   .venv\Scripts\Activate.ps1
   
   # On Windows CMD:
   .venv\Scripts\activate.bat
   
   # On Mac/Linux:
   source .venv/bin/activate
   ```

3. Install dependencies (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

   This will:
   - Create all necessary tables in Supabase
   - Seed initial tickers (AAPL, MSFT, GOOGL, etc.)

   **Expected output:**
   ```
   Creating tables...
   Tables created successfully
   Added ticker: AAPL - Apple Inc.
   Added ticker: MSFT - Microsoft Corporation
   ...
   Tickers seeded successfully
   Database initialization complete!
   ```

---

## 🤖 Step 4: Train the ML Model

1. Still in the `backend` folder, run:
   ```bash
   python train_model.py
   ```

   This will:
   - Fetch historical data from the database
   - Compute ML features
   - Train a RandomForest model
   - Save the model to `backend/models/classifier.pkl`
   - Save metrics to `backend/models/model_metrics.json`

   **Note:** This may take a few minutes the first time as it needs to fetch data from APIs.

---

## 🚀 Step 5: Start the Application

### Start Backend

1. In the `backend` folder, run:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. You should see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   Model inference service initialized
   ```

3. Test the API:
   - Open browser: http://localhost:8000
   - You should see: `{"message": "News & Sentiment Driven Stock Explorer API"}`
   - Test tickers: http://localhost:8000/api/tickers

### Start Frontend

1. Open a **new terminal window**
2. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```

3. Install dependencies (if not already done):
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. You should see:
   ```
   VITE v5.x.x  ready in xxx ms
   ➜  Local:   http://localhost:5173/
   ```

6. Open http://localhost:5173 in your browser

---

## ✅ Verification Checklist

- [ ] Supabase project created and connection string obtained
- [ ] Finnhub API key obtained
- [ ] NewsAPI.org API key obtained
- [ ] OpenAI API key obtained
- [ ] Backend `.env` file created with all keys
- [ ] Frontend `.env.local` file created
- [ ] Database initialized (`python init_db.py` ran successfully)
- [ ] ML model trained (`python train_model.py` ran successfully)
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Can select a ticker in the frontend
- [ ] Can fetch analysis for a date range

---

## 🐛 Troubleshooting

### Database Connection Errors

**Error:** `DATABASE_URL not set in environment`
- **Solution:** Make sure `.env` file exists in `backend/` folder and contains `DATABASE_URL`

**Error:** `Connection refused` or `could not connect to server`
- **Solution:** 
  - Verify your Supabase project is active
  - Check the connection string is correct
  - Make sure you replaced `[YOUR-PASSWORD]` with your actual password
  - Check if your IP needs to be whitelisted in Supabase (usually not needed)

### API Key Errors

**Error:** `FINNHUB_API_KEY not set in environment`
- **Solution:** Add `FINNHUB_API_KEY=your_key` to `backend/.env`

**Error:** `NEWSAPI_API_KEY not set in environment`
- **Solution:** Add `NEWSAPI_API_KEY=your_key` to `backend/.env`

**Error:** `OPENAI_API_KEY not set in environment`
- **Solution:** Add `OPENAI_API_KEY=sk-your_key` to `backend/.env`

### Rate Limit Errors

**Finnhub:** 60 calls/minute
- **Solution:** Wait a minute and try again, or upgrade your plan

**NewsAPI:** 100 requests/day (free tier)
- **Solution:** Wait until next day, or upgrade to a paid plan

**OpenAI:** Rate limits depend on your account tier
- **Solution:** Check your usage in OpenAI dashboard, add payment method if needed

### Model Not Found

**Error:** `Model metrics not found. Train the model first.`
- **Solution:** Run `python train_model.py` in the `backend/` folder

### Frontend Can't Connect to Backend

**Error:** Network error or CORS error
- **Solution:** 
  - Make sure backend is running on http://localhost:8000
  - Check `VITE_API_BASE_URL` in `frontend/.env.local` is set to `http://localhost:8000`
  - Restart the frontend dev server after changing `.env.local`

---

## 📚 Additional Resources

- **Supabase Docs:** https://supabase.com/docs
- **Finnhub API Docs:** https://finnhub.io/docs/api
- **NewsAPI Docs:** https://newsapi.org/docs
- **OpenAI API Docs:** https://platform.openai.com/docs

---

## 💡 Tips

1. **Start with free tiers** - All services offer free tiers that are sufficient for development
2. **Monitor API usage** - Keep an eye on your API usage, especially OpenAI costs
3. **Use environment variables** - Never hardcode API keys in your code
4. **Test incrementally** - Test each API individually before running the full app
5. **Check logs** - If something fails, check the terminal output for detailed error messages

---

## 🎉 You're All Set!

Once everything is configured, you should be able to:
- Select a stock ticker (e.g., AAPL)
- Choose a date range
- View price charts with sentiment overlay
- Browse news articles with AI-generated sentiment scores
- See ML-based insights about sentiment's predictive power

Happy exploring! 🚀

