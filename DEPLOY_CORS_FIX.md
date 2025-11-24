# Deploy CORS Fix - Critical Steps

## Problem

The CORS configuration wasn't working because:
1. FastAPI CORS doesn't support wildcards in `allow_origins`
2. The Vercel domain needs to be explicitly allowed
3. Code changes need to be deployed to Render

## Solution

I've updated `backend/app.py` to:
- ✅ Include your Vercel domain directly in the code
- ✅ Use `allow_origin_regex` to match any `*.vercel.app` domain
- ✅ Better environment variable handling

## Deploy the Fix (5 minutes)

### Step 1: Commit the Changes

```bash
# Navigate to project root
cd C:\Users\yash\OneDrive\Desktop\News-Sentiment-Driven-Stock-Explorer

# Check what changed
git status

# Add the changes
git add backend/app.py

# Commit
git commit -m "Fix: Update CORS to allow Vercel domains using regex pattern"

# Push to GitHub
git push
```

### Step 2: Render Will Auto-Deploy

Render is connected to your GitHub repo, so it will automatically:
1. Detect the push
2. Start a new deployment
3. Deploy the updated code

**Wait 2-3 minutes** for the deployment to complete.

### Step 3: Verify Deployment

1. **Check Render Dashboard:**
   - Go to: https://dashboard.render.com/web/srv-d4gc5cjuibrs73fd0gcg
   - Click **"Events"** tab
   - Look for the latest deployment
   - Wait until status shows **"Live"**

2. **Check Render Logs:**
   - Click **"Logs"** tab
   - Look for this line:
     ```
     CORS allowed origins: ['http://localhost:5173', 'http://localhost:3000', 'https://news-sentiment-driven-stock-explore.vercel.app']
     ```
   - This confirms the CORS configuration loaded correctly

### Step 4: Test Your Website

1. **Open your Vercel site:**
   - https://news-sentiment-driven-stock-explore.vercel.app

2. **Open browser DevTools** (F12) → **Console** tab

3. **Refresh the page**

4. **Verify:**
   - ✅ No CORS errors in console
   - ✅ Ticker dropdown loads with stock symbols
   - ✅ "Model Details" section loads (not "Failed to fetch")

---

## What Changed in the Code

The key fix is using `allow_origin_regex`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # ← This matches any Vercel domain!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This allows **any** Vercel deployment (like `https://*.vercel.app`) without needing to list each one explicitly.

---

## If It Still Doesn't Work

### Check 1: Verify Code is Deployed

1. Go to Render → **Logs** tab
2. Look for the startup message with CORS origins
3. If you don't see the updated origins, the deployment might not have completed

### Check 2: Force a Redeploy

1. Go to Render → **Settings** tab
2. Scroll to bottom
3. Click **"Clear build cache & deploy"**
4. Wait for deployment

### Check 3: Verify Backend is Running

1. Visit: https://news-sentiment-driven-stock-explorer.onrender.com/health
2. Should return: `{"status":"ok"}`

### Check 4: Browser Cache

1. Hard refresh: **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)
2. Or open in Incognito/Private window

---

**After deploying, your website should work!** 🎉

The regex pattern `https://.*\.vercel\.app` will match any Vercel deployment, so this fix should work for all your Vercel previews and production deployments.

