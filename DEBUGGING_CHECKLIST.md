# Comprehensive Debugging Checklist

Use this checklist to gather all information needed to diagnose issues.

## 1. Backend Logs (Render)

**What to share:**
- Full recent logs from Render dashboard (last 50-100 lines)
- Any error messages or stack traces
- Look for:
  - Database connection errors
  - API endpoint errors (500, 404, etc.)
  - Import errors
  - Date-related errors
  - yfinance errors

**How to get:**
1. Go to Render dashboard → Your service → Logs tab
2. Copy the last 50-100 lines
3. Share them here

---

## 2. Frontend Console Errors (Browser)

**What to share:**
- Open browser DevTools (F12)
- Go to Console tab
- Copy all errors (red messages)
- Also check Network tab for failed API requests

**What to look for:**
- CORS errors
- 404/500 errors from API
- JavaScript errors
- Failed fetch requests

---

## 3. API Endpoint Tests

**Test these endpoints directly:**

```bash
# Health check
curl https://your-backend.onrender.com/health

# Tickers
curl https://your-backend.onrender.com/api/tickers

# Summary (replace with your actual dates)
curl "https://your-backend.onrender.com/api/summary?ticker=AAPL&start_date=2025-10-22&end_date=2025-11-21"

# Model metrics
curl https://your-backend.onrender.com/api/model-metrics
```

**Share:**
- The full response (or error) from each endpoint
- Status codes
- Response bodies

---

## 4. Frontend URL and Behavior

**What to share:**
- Your Vercel frontend URL
- What happens when you:
  - Load the page
  - Select a ticker
  - Click "Analyze"
  - What error messages appear (if any)
  - What data is missing or incorrect

---

## 5. Database Status

**Check Supabase:**
- Can you access your Supabase dashboard?
- Do you see data in:
  - `daily_prices` table
  - `news_articles` table
  - `tickers` table
- What date ranges do you have data for?

**Share:**
- Approximate row counts for each table
- Date ranges of your data

---

## 6. Environment Variables

**Backend (Render):**
Check that these are set:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `ALPHAVANTAGE_API_KEY`
- `OPENAI_API_KEY` (optional)
- `ALLOWED_ORIGINS` (optional)

**Frontend (Vercel):**
Check that this is set:
- `VITE_API_BASE_URL` (should be your Render backend URL)

**Share:**
- Which variables are set (don't share the actual values!)
- Any that are missing

---

## 7. Specific Issues to Describe

For each issue, describe:
1. **What you expect to happen**
2. **What actually happens**
3. **When it happens** (on page load, after clicking Analyze, etc.)
4. **Error messages** (exact text)

**Common issues to check:**
- [ ] Frontend doesn't load
- [ ] Ticker dropdown is empty
- [ ] Clicking "Analyze" does nothing
- [ ] Clicking "Analyze" shows error
- [ ] No price data displayed
- [ ] No news articles displayed
- [ ] Sentiment distribution is wrong
- [ ] Charts don't render
- [ ] Model metrics don't show

---

## 8. Screenshots

**Helpful screenshots:**
- Frontend showing the error/problem
- Browser console with errors
- Network tab showing failed requests
- Render logs showing errors

---

## Quick Test Script

Run this locally to test your backend:

```python
# test_backend.py
import requests
from datetime import date, timedelta

BASE_URL = "https://your-backend.onrender.com"  # Replace with your URL

# Test health
print("Testing /health...")
r = requests.get(f"{BASE_URL}/health")
print(f"Status: {r.status_code}, Response: {r.json()}")

# Test tickers
print("\nTesting /api/tickers...")
r = requests.get(f"{BASE_URL}/api/tickers")
print(f"Status: {r.status_code}, Response: {r.json()}")

# Test summary
print("\nTesting /api/summary...")
end_date = date.today()
start_date = end_date - timedelta(days=30)
r = requests.get(f"{BASE_URL}/api/summary", params={
    "ticker": "AAPL",
    "start_date": start_date.isoformat(),
    "end_date": end_date.isoformat()
})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Price points: {len(data.get('price_series', []))}")
    print(f"Articles: {data.get('n_articles', 0)}")
    print(f"Sentiment series: {len(data.get('sentiment_series', []))}")
else:
    print(f"Error: {r.text}")
```

---

## What I Need Most

**Priority 1 (Most Important):**
1. Backend logs from Render (showing actual errors)
2. Frontend console errors from browser
3. What happens when you click "Analyze" (step by step)

**Priority 2:**
4. API endpoint test results (curl commands above)
5. Screenshots of the frontend showing the issue

**Priority 3:**
6. Environment variables checklist
7. Database status

Share as much as you can, and I'll help diagnose and fix all the issues!

