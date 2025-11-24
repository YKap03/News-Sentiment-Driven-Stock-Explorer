# Fix CORS Error - Empty Website

## Problem

Your Vercel frontend shows "Loading..." and nothing loads. The browser console shows CORS errors like:

```
Access to fetch at 'https://news-sentiment-driven-stock-explorer.onrender.com/api/tickers' 
from origin 'https://news-sentiment-driven-stock-explore.vercel.app' 
has been blocked by CORS policy
```

This means the backend isn't allowing requests from your Vercel frontend.

## Solution

You need to add your Vercel domain to the backend's CORS allowed origins.

### Quick Fix (2 minutes)

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com
   - Click on your backend service

2. **Go to Environment Tab:**
   - Click **"Environment"** in the left sidebar

3. **Add/Update ALLOWED_ORIGINS:**
   - Look for `ALLOWED_ORIGINS` variable (or create it if it doesn't exist)
   - Set the value to your Vercel URL:
     ```
     https://news-sentiment-driven-stock-explore.vercel.app
     ```
   - **If you want to allow multiple Vercel deployments**, use comma-separated:
     ```
     https://news-sentiment-driven-stock-explore.vercel.app,http://localhost:5173
     ```

4. **Save Changes:**
   - Click **"Save Changes"** button
   - Render will automatically redeploy (takes ~1 minute)

5. **Wait for Redeploy:**
   - Check the "Events" tab to see the redeploy progress
   - Wait until it says "Live"

6. **Test:**
   - Refresh your Vercel page: https://news-sentiment-driven-stock-explore.vercel.app
   - The ticker dropdown should now load!

---

## Alternative: Allow All Origins (Less Secure - For Testing Only)

If you want to allow all origins (not recommended for production), you can set:

```
ALLOWED_ORIGINS=*
```

**Warning:** This is less secure and should only be used for testing. For production, specify exact domains.

---

## Verify It's Working

1. **Open your Vercel site:** https://news-sentiment-driven-stock-explore.vercel.app
2. **Open browser DevTools:** Press F12
3. **Go to Console tab:**
   - You should NOT see CORS errors anymore
   - Ticker dropdown should show stock symbols (AAPL, MSFT, etc.)
4. **Go to Network tab:**
   - Click "Analyze" button
   - You should see successful API calls (status 200)

---

## Why This Happened

FastAPI's CORS middleware doesn't support wildcard patterns like `https://*.vercel.app`. You need to specify the exact domain(s) in the `ALLOWED_ORIGINS` environment variable.

The code I just updated will use the environment variable if set, otherwise default to localhost for development.

---

## After Fixing CORS

Once CORS is fixed, you may still need to:
1. **Initialize your database** (if you haven't already):
   - Follow instructions in `INIT_DB_LOCALLY.md` or `QUICK_DATABASE_SETUP.md`
   - Run `python init_db.py` locally to seed tickers

2. **Train the model** (optional):
   - Run `python train_model.py` locally
   - Or it will train automatically when needed

---

**That's it! Your website should now work correctly.** 🎉

