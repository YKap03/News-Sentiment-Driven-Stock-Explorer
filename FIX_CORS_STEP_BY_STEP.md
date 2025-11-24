# Fix CORS Error - Step by Step

## Issue

Even though you've added `ALLOWED_ORIGINS`, the CORS errors persist because:

1. **Trailing slash issue**: Your value has a trailing slash: `https://news-sentiment-driven-stock-explore.vercel.app/`
2. **Service needs redeploy**: After changing environment variables, Render needs to redeploy

## Solution - Follow These Exact Steps

### Step 1: Fix the Environment Variable Value

1. **Go to Render Dashboard** → Your service → **Environment** tab
2. **Click "Edit"** button (top right of Environment Variables section)
3. **Find `ALLOWED_ORIGINS`** in the list
4. **Remove the trailing slash** from the value:
   - ❌ **Wrong**: `https://news-sentiment-driven-stock-explore.vercel.app/`
   - ✅ **Correct**: `https://news-sentiment-driven-stock-explore.vercel.app`
5. **Click "Save"** at the bottom

### Step 2: Trigger a Manual Redeploy

**This is critical!** After changing environment variables, you must redeploy:

1. **In Render Dashboard**, go to your service
2. Click **"Manual Deploy"** dropdown (top right)
3. Select **"Deploy latest commit"**
4. **Wait for deployment** (usually 1-2 minutes)
5. Watch the **"Events"** tab to see deployment progress
6. Wait until it says **"Live"**

### Step 3: Verify It's Fixed

1. **Wait 1-2 minutes** after deployment completes
2. **Open your Vercel site**: https://news-sentiment-driven-stock-explore.vercel.app
3. **Open browser DevTools** (F12) → **Console** tab
4. **Refresh the page**
5. **Check:**
   - ✅ Should NOT see CORS errors anymore
   - ✅ Ticker dropdown should load with stock symbols
   - ✅ "Model Details" should load (not show "Failed to fetch")

---

## Alternative: Quick Redeploy Method

If you want to force a redeploy without waiting:

1. Go to **Settings** tab in Render
2. Scroll to bottom
3. Click **"Clear build cache & deploy"**

---

## Check Render Logs

To verify the CORS origins are loaded correctly:

1. Go to Render → **Logs** tab
2. Look for the line that says: `CORS allowed origins: [...]`
3. It should show: `CORS allowed origins: ['https://news-sentiment-driven-stock-explore.vercel.app']`

If you don't see your Vercel URL in that list, the environment variable isn't being read correctly.

---

## Still Not Working?

If it's still not working after redeploy:

1. **Double-check the environment variable**:
   - Value should be: `https://news-sentiment-driven-stock-explore.vercel.app`
   - No trailing slash
   - No extra spaces

2. **Check Render logs** for the CORS origins message

3. **Try clearing browser cache**:
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

4. **Verify your backend is actually running**:
   - Visit: https://news-sentiment-driven-stock-explorer.onrender.com/health
   - Should return: `{"status": "ok"}`

---

**After fixing the trailing slash and redeploying, it should work!** 🎉

