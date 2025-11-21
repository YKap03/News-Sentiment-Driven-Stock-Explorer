# Complete Deployment Guide: Step-by-Step Instructions

This guide will walk you through deploying the News & Sentiment Driven Stock Explorer so users can access it via a Vercel URL.

---

## 📋 Prerequisites Checklist

Before starting, you'll need:
- [ ] A GitHub account (free)
- [ ] Your code pushed to a GitHub repository
- [ ] About 30-45 minutes to complete the setup

---

## 🔵 Step 1: Create Accounts & Get API Keys

### 1.1 Alpha Vantage API Key (Required for News Data)

1. Go to https://www.alphavantage.co/support/#api-key
2. Fill out the form:
   - **Full Name**: Your name
   - **Email**: Your email
   - **Organization**: Your organization/name
   - **Use Case**: Select "Market Research" or "Educational"
3. Click **"GET FREE API KEY"**
4. **Copy and save your API key** (e.g., `ABC123XYZ789`)
   - ⚠️ **Save this somewhere safe** - you'll need it later

**Status**: Free tier allows 5 API calls/minute, 500 calls/day

---

### 1.2 OpenAI API Key (Optional, but Recommended)

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click **"Create new secret key"**
4. Give it a name (e.g., "Stock Explorer Sentiment")
5. **Copy and save your API key** (starts with `sk-...`)
   - ⚠️ **You can only see it once** - save it immediately!

**Status**: Pay-per-use (usually $0.01-0.02 per 1000 articles)

**Note**: This is optional - Alpha Vantage provides sentiment analysis, but OpenAI can enrich it.

---

### 1.3 Supabase Account & Database (Required)

1. Go to https://supabase.com
2. Click **"Start your project"** or **"Sign up"**
3. Sign up with GitHub (easiest) or email
4. Click **"New Project"**
5. Fill out the form:
   - **Name**: `news-stock-explorer` (or any name)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you (e.g., US East, EU West)
   - **Plan**: Select **"Free"** (sufficient for this project)
6. Click **"Create new project"**
7. Wait 2-3 minutes for the database to provision

**Once your project is ready:**

8. Go to **Settings** → **API** (in the left sidebar)
9. **Copy these values** (you'll need them later):
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon public** key: Long string starting with `eyJ...`
   - ⚠️ **Save both of these**

10. **Create the database tables:**
    - Go to **SQL Editor** (in left sidebar)
    - Click **"New query"**
    - Open `backend/db/init_supabase_tables.sql` from your code
    - Copy **all the SQL** from that file
    - Paste it into the SQL Editor
    - Click **"Run"** (or press Ctrl+Enter)
    - You should see "Success. No rows returned"

11. **Run migration scripts** (if they exist):
    - Repeat the process for `backend/db/migrate_add_is_relevant.sql`
    - Repeat for `backend/db/migrate_add_relevance_score.sql`
    - (Run each SQL file one at a time)

**✅ Supabase Setup Complete!**

---

## 🟢 Step 2: Deploy Backend on Render

### 2.1 Create Render Account

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended) or email
4. Verify your email if needed

### 2.2 Create Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. If prompted, **connect your GitHub account** (authorize Render)
3. **Select your repository**: Choose the `News-Sentiment-Driven-Stock-Explorer` repo
4. Click **"Connect"**

### 2.3 Configure Backend Service

Fill out the form with these settings:

- **Name**: `news-stock-backend` (or any name - this becomes part of your URL)
- **Region**: Choose closest to your users (e.g., `Oregon (US West)`)
- **Branch**: `main` (or your default branch name)
- **Root Directory**: `backend` ⚠️ **IMPORTANT!**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Plan**: Select **"Free"** (or upgrade if you need more)

Click **"Create Web Service"**

### 2.4 Set Environment Variables

While your service is deploying, go to the **Environment** tab (left sidebar):

Click **"Add Environment Variable"** and add each of these:

1. **SUPABASE_URL**
   - Key: `SUPABASE_URL`
   - Value: Your Supabase Project URL (from Step 1.3)
   - Example: `https://xxxxxxxxxxxxx.supabase.co`

2. **SUPABASE_KEY**
   - Key: `SUPABASE_KEY`
   - Value: Your Supabase anon public key (from Step 1.3)
   - Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (long string)

3. **ALPHAVANTAGE_API_KEY**
   - Key: `ALPHAVANTAGE_API_KEY`
   - Value: Your Alpha Vantage API key (from Step 1.1)
   - Example: `ABC123XYZ789`

4. **OPENAI_API_KEY** (Optional but recommended)
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (from Step 1.2)
   - Example: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

5. **ALLOWED_ORIGINS** (Optional - add after frontend is deployed)
   - Key: `ALLOWED_ORIGINS`
   - Value: Leave this for now - we'll add it after frontend deployment
   - Or set to: `https://*.vercel.app` (allows any Vercel domain)

Click **"Save Changes"** after adding each variable.

### 2.5 Wait for Deployment

1. Go back to the **"Logs"** tab
2. Watch the deployment progress
3. Wait for it to complete (usually 2-5 minutes)
4. Once deployed, you'll see a URL like: `https://news-stock-backend.onrender.com`

### 2.6 Test Backend

1. Copy your backend URL (e.g., `https://news-stock-backend.onrender.com`)
2. Test these URLs in your browser:
   - `https://your-backend.onrender.com/health` → Should show `{"status":"ok"}`
   - `https://your-backend.onrender.com/` → Should show API message
   - `https://your-backend.onrender.com/api/tickers` → Should show JSON with tickers (may be empty initially)

**✅ Backend Deployed!**

### 2.7 Initialize Database (One-time setup)

**Option A: Using Render Shell (Recommended)**

1. In Render dashboard → Your service → **"Shell"** tab
2. Click **"Connect"** to open a shell
3. Run these commands:
   ```bash
   python init_db.py
   ```
   (This creates the initial tickers like AAPL, MSFT, etc.)

4. Train the ML model:
   ```bash
   python train_model.py
   ```
   (This trains the model on existing data)

**Option B: Run Locally (Alternative)**

1. On your local machine, create `backend/.env` file:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key
   ALPHAVANTAGE_API_KEY=your-alpha-vantage-key
   OPENAI_API_KEY=your-openai-key
   ```

2. Run these commands locally:
   ```bash
   cd backend
   python init_db.py
   python train_model.py
   ```
   (This connects to your Supabase database using your local `.env` file)

**✅ Database Initialized!**

---

## 🟣 Step 3: Deploy Frontend on Vercel

### 3.1 Create Vercel Account

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Sign up with GitHub (recommended) - it's easier
4. Authorize Vercel to access your GitHub repos

### 3.2 Import Your Project

1. In Vercel dashboard, click **"Add New..."** → **"Project"**
2. You'll see a list of your GitHub repositories
3. Find and click **"Import"** next to `News-Sentiment-Driven-Stock-Explorer`

### 3.3 Configure Frontend Project

Vercel should auto-detect Vite, but verify these settings:

- **Framework Preset**: `Vite` (should be auto-detected)
- **Root Directory**: Click **"Edit"** and set to `frontend` ⚠️ **IMPORTANT!**
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `dist` (auto-detected)
- **Install Command**: `npm install` (auto-detected)

### 3.4 Set Environment Variable

Before deploying, click **"Environment Variables"** and add:

- **Key**: `VITE_API_BASE_URL`
- **Value**: Your Render backend URL (from Step 2.6)
  - Example: `https://news-stock-backend.onrender.com`
  - ⚠️ **Include `https://`** - don't forget the protocol!
- **Environment**: Select **"Production"** (or all environments)

Click **"Save"**

### 3.5 Deploy

1. Click **"Deploy"** button
2. Wait for the build to complete (usually 1-2 minutes)
3. Once deployed, Vercel will show you a URL like: `https://news-sentiment-driven-stock-explorer.vercel.app`

**✅ Frontend Deployed!**

### 3.6 Update Backend CORS (Important!)

Now that your frontend is deployed, update the backend to allow requests from your Vercel domain:

1. Go back to **Render** dashboard → Your backend service → **Environment** tab
2. Find `ALLOWED_ORIGINS` environment variable
3. Update it with your Vercel URL:
   - Value: `https://your-project.vercel.app`
   - Or keep it as `https://*.vercel.app` to allow all Vercel deployments
4. Click **"Save Changes"**
5. Render will automatically redeploy (takes ~1 minute)

**Note**: If you didn't set `ALLOWED_ORIGINS` earlier, you can leave it unset - the default includes `https://*.vercel.app` which will work.

---

## ✅ Step 4: Test Your Deployment

### 4.1 Test the Frontend

1. Open your Vercel URL (e.g., `https://your-project.vercel.app`)
2. The website should load
3. Try selecting a ticker (e.g., AAPL)
4. Select a date range
5. Click "Analyze" or similar button

### 4.2 Verify API Calls

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. In your app, trigger an API call (select ticker, etc.)
4. You should see requests to your Render backend URL
5. Check that they return 200 status codes

### 4.3 Troubleshooting

**Frontend shows errors:**
- Check browser console (F12 → Console tab)
- Verify `VITE_API_BASE_URL` is set correctly in Vercel
- Make sure it includes `https://`

**CORS errors in browser console:**
- Go to Render → Environment → Check `ALLOWED_ORIGINS`
- Make sure your Vercel URL is included (or use `https://*.vercel.app`)

**Backend returns errors:**
- Check Render logs (Render dashboard → Logs tab)
- Verify all environment variables are set correctly
- Make sure database tables were created in Supabase

**No data showing:**
- Check if tickers exist in database (test `/api/tickers` endpoint)
- Make sure you ran `python init_db.py` (Step 2.7)
- Check if you have news data (may take time for first API calls)

---

## 🔗 Step 5: Share Your App

Once everything works:

1. **Share your Vercel URL** with users:
   - Example: `https://your-project.vercel.app`
   - Anyone with this link can access your app!

2. **Optional: Add Custom Domain**
   - In Vercel dashboard → Settings → Domains
   - Add your custom domain (e.g., `stockexplorer.com`)
   - Follow Vercel's DNS instructions

3. **Monitor Usage:**
   - Render dashboard shows backend usage
   - Vercel dashboard shows frontend traffic
   - Supabase dashboard shows database usage

---

## 📊 Account Summary

Here's what accounts you created:

| Service | Account Type | Purpose | Cost |
|---------|--------------|---------|------|
| **GitHub** | Free | Code hosting | Free |
| **Supabase** | Free tier | Database | Free (up to 500MB) |
| **Render** | Free tier | Backend hosting | Free (with limits) |
| **Vercel** | Free tier | Frontend hosting | Free |
| **Alpha Vantage** | Free tier | News API | Free (500 calls/day) |
| **OpenAI** | Pay-per-use | Sentiment enrichment | ~$0.01-0.02/1000 articles |

**Total Cost**: $0 per month (or ~$1-5/month if you use OpenAI extensively)

---

## 🎉 You're Done!

Your app is now live and accessible to users via the Vercel link!

**Quick Links:**
- Frontend: `https://your-project.vercel.app`
- Backend API: `https://your-backend.onrender.com`
- Backend Health: `https://your-backend.onrender.com/health`

---

## 📝 Maintenance Notes

**Regular Tasks:**
- Monitor Render logs for errors
- Check Supabase database size (free tier: 500MB)
- Monitor API usage (Alpha Vantage: 500 calls/day limit)

**If Backend Goes to Sleep:**
- Free Render services spin down after 15 minutes of inactivity
- First request may take 30-60 seconds to wake up
- Consider upgrading to paid plan if you need always-on

**Updating the App:**
- Push changes to GitHub
- Render and Vercel will automatically redeploy
- No manual deployment needed!

---

## 🆘 Need Help?

Common issues and solutions:

**Issue**: Backend returns 502 errors  
**Solution**: Check Render logs, verify environment variables are set

**Issue**: Frontend can't connect to backend  
**Solution**: Check `VITE_API_BASE_URL` in Vercel, verify CORS settings

**Issue**: No tickers showing  
**Solution**: Run `python init_db.py` from Render shell or locally

**Issue**: "Model not found" errors  
**Solution**: Run `python train_model.py` from Render shell or locally

For more troubleshooting, see the main `README.md` file.

