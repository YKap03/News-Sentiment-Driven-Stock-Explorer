# Fix for Render Build Error: pandas + Python 3.13

## Problem

Render is using **Python 3.13.4**, but **pandas 2.1.3** doesn't support Python 3.13.

**Error:** `too few arguments to function '_PyLong_AsByteArray'`

## Solution Options

### ✅ Option 1: Use runtime.txt (Recommended if keeping pandas 2.1.3)

**Created:** `backend/runtime.txt` with `python-3.12.8`

**How it works:**
- Render automatically detects `runtime.txt` in your root directory (`backend/`)
- It will use Python 3.12.8 instead of 3.13.4
- pandas 2.1.3 works perfectly with Python 3.12

**To apply:**
1. Commit and push `runtime.txt`:
   ```bash
   git add backend/runtime.txt
   git commit -m "Add runtime.txt to use Python 3.12.8"
   git push
   ```

2. **Important:** Clear Render's build cache:
   - Go to Render dashboard → Your service
   - Settings → Scroll down to "Clear build cache"
   - Click "Clear build cache"
   - Then click "Manual Deploy" → "Clear build cache & deploy"

3. Check logs - should now show Python 3.12.8

### ✅ Option 2: Upgrade pandas (Recommended - simpler)

**Update `backend/requirements.txt`:**
```txt
pandas>=2.2.3  # Instead of pandas==2.1.3
```

**Benefits:**
- Works with Python 3.13 (no runtime.txt needed)
- Latest pandas features and bug fixes
- Simpler - one less file to manage

**To apply:**
1. Update `requirements.txt`:
   ```txt
   pandas>=2.2.3
   ```

2. Commit and push:
   ```bash
   git add backend/requirements.txt
   git commit -m "Upgrade pandas to 2.2.3+ for Python 3.13 support"
   git push
   ```

3. Render will auto-deploy

## Why runtime.txt might not work immediately

If `runtime.txt` doesn't seem to work:

1. **Location:** Make sure it's at `backend/runtime.txt` (which it is)
2. **Build cache:** Render caches the Python version - **clear the build cache** (most important!)
3. **Detection:** Render detects `runtime.txt` at the start of build - if Python was already installed from cache, it won't see it

**Solution:** Always clear build cache after adding/updating `runtime.txt`

## Recommendation

I recommend **Option 2** (upgrade pandas) because:
- ✅ Simpler - no need to manage Python version
- ✅ Latest features
- ✅ No cache clearing needed
- ✅ Works immediately

But **Option 1** (runtime.txt) is fine if you want to stick with pandas 2.1.3.

## Quick Fix Steps

**If using runtime.txt:**
1. File is already created: `backend/runtime.txt`
2. Push to GitHub
3. **Clear build cache in Render** ← VERY IMPORTANT!
4. Redeploy

**If upgrading pandas:**
1. Change `pandas==2.1.3` to `pandas>=2.2.3` in `requirements.txt`
2. Push to GitHub
3. Render auto-deploys

