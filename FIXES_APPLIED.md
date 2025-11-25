# Fixes Applied - November 24, 2025

## Issues Identified and Fixed

### 1. ✅ Environment Variables Not Loading Locally

**Problem:** The `quick_diagnostic.py` script wasn't loading the `.env` file, so it reported all environment variables as missing even though they existed.

**Fix:** Added `python-dotenv` loading at the start of the diagnostic script to automatically load `.env` files for local development.

**File Changed:** `backend/quick_diagnostic.py`

---

### 2. ✅ yfinance Still Being Called for Future Dates

**Problem:** Even though we fixed `ensure_price_data` to check the database first, it was still trying to fetch future dates (2025-10-25, 2025-11-01, etc.) from yfinance, causing "possibly delisted" errors.

**Root Cause:** The missing date detection was running for ALL dates in the requested range, including future dates, before filtering them out.

**Fix:** 
- Filter out future dates from `missing_dates` BEFORE processing them
- Only check for missing dates that are `<= today`
- Added clear logging to indicate when future dates are being skipped

**File Changed:** `backend/services/data_refresh.py`

**Key Change:**
```python
# OLD: Checked all dates, then filtered
while current <= end_date:
    if current not in existing_dates:
        missing_dates.append(current)

# NEW: Only check non-future dates
while current <= end_date:
    if current <= today and current not in existing_dates:
        missing_dates.append(current)
```

---

### 3. ✅ Sentiment Distribution Showing 0 for Negative Articles

**Problem:** Backend shows "negative: 9" articles, but frontend chart shows 0 for "Very Negative" and "Negative" categories.

**Potential Issues:**
- Case sensitivity in label matching
- Articles not being passed correctly to the chart component
- Label not being sent from backend

**Fixes Applied:**
1. Made label matching case-insensitive (e.g., "Bearish" and "bearish" both work)
2. Added debug logging to frontend (console.log in development mode)
3. Added backend debug logging to show label distribution
4. Verified backend is sending `sentiment_label` in ArticleResponse

**Files Changed:**
- `frontend/src/components/SentimentDistributionChart.tsx` - Case-insensitive matching + debug logging
- `backend/app.py` - Enhanced debug logging for sentiment labels

**Next Steps for Debugging:**
- Check browser console (F12) when viewing the chart
- Look for `[SentimentDistributionChart]` log messages
- Verify articles have `sentiment_label` field populated

---

## Testing Checklist

After deploying these fixes, verify:

- [ ] Run `python backend/quick_diagnostic.py` locally - should now detect environment variables
- [ ] Check Render logs - should NOT see yfinance errors for future dates
- [ ] Check browser console - should see sentiment distribution debug logs
- [ ] Verify sentiment distribution chart shows negative articles correctly
- [ ] Test with different date ranges to ensure no yfinance calls for future dates

---

## Deployment Notes

1. **Backend (Render):**
   - The fixes to `data_refresh.py` will prevent yfinance calls for future dates
   - Enhanced logging will help debug sentiment issues
   - No environment variable changes needed

2. **Frontend (Vercel):**
   - The sentiment chart fix will make label matching case-insensitive
   - Debug logging will only appear in development mode
   - No breaking changes

---

## Expected Behavior After Fixes

1. **No yfinance errors:** Should only see `[INFO]` messages about skipping future dates, no "possibly delisted" errors
2. **Sentiment distribution:** Should correctly show negative articles based on:
   - Alpha Vantage labels ("Bearish", "Somewhat-Bearish") → "Very Negative" / "Negative"
   - Numeric scores (< -0.1) → "Negative" or "Very Negative"
3. **Diagnostic script:** Should correctly detect environment variables when run locally

---

## If Issues Persist

1. **Sentiment still showing 0:**
   - Check browser console for debug logs
   - Verify articles in API response have `sentiment_label` field
   - Check if labels match exactly (case-insensitive now)

2. **Still seeing yfinance errors:**
   - Check Render logs for the exact date ranges being requested
   - Verify `date.today()` is correct on Render (should be 2024, not 2025)
   - Check if `ensure_price_data` is being called from other places

3. **Environment variables still not detected:**
   - Verify `.env` file exists in `backend/` directory
   - Check that `python-dotenv` is installed: `pip install python-dotenv`
   - Try running: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('SUPABASE_URL'))"`

