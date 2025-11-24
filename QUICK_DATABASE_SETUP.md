# Quick Database Setup Guide

## ✅ Step 1: Create Tables in Supabase (5 minutes)

1. **Go to Supabase SQL Editor:**
   - Visit: https://supabase.com/dashboard
   - Select your project
   - Click **"SQL Editor"** in left sidebar
   - Click **"New query"**

2. **Run the main SQL script:**
   - Open `backend/db/init_supabase_tables.sql` from your code
   - Copy ALL the SQL
   - Paste into Supabase SQL Editor
   - Click **"Run"** (green button or Ctrl+Enter)
   - ✅ Should see "Success. No rows returned"

3. **Run migration script (adds is_relevant column):**
   - Open `backend/db/migrate_add_is_relevant.sql` 
   - Copy ALL the SQL
   - Paste into SQL Editor (new query)
   - Click **"Run"**
   - ✅ Should see "Success" messages

**✅ Tables are now created!**

---

## ✅ Step 2: Seed Tickers (Run Locally)

**Note:** Render Shell is not available on the free tier. Run the initialization locally - it connects to the same Supabase database!

### 2.1 Get Environment Variables from Render

1. Go to Render dashboard → Your service → **Environment** tab
2. Click the **eye icon** 👁️ next to each variable to reveal values
3. You'll need: `SUPABASE_URL` and `SUPABASE_KEY` (others are optional for this step)

### 2.2 Create Local `.env` File

1. Navigate to `backend/` folder on your computer
2. Create a file named `.env` (not `.env.txt`)
3. Add these lines (use values from Render):

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
ALPHAVANTAGE_API_KEY=your-alpha-vantage-key
OPENAI_API_KEY=your-openai-key
```

**⚠️ Important:** Copy the exact values from Render (click eye icon to see them).

### 2.3 Run Initialization Locally

**Open terminal/PowerShell in the `backend/` folder:**

```bash
# Make sure you're in backend/ directory
cd backend

# (Optional) Create virtual environment if you don't have one
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Mac/Linux:
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run initialization script
python init_db.py
```

**Expected output:**
```
Initializing database with Supabase...
Added ticker: AAPL - Apple Inc.
Added ticker: MSFT - Microsoft Corporation
...
Tickers seeded successfully
Database initialization complete!
```

### 2.4 (Optional) Train the Model

```bash
python train_model.py
```

**✅ Database is ready!**

**Why this works:** Your local script connects to the same Supabase database that Render uses - it's an external database, so running locally works perfectly!

---

## ✅ Step 3: Test It Works

Visit in browser:
- `https://your-service.onrender.com/api/tickers`
- Should return JSON with tickers list

---

**That's it! Your database is now initialized and ready to use.** 🎉

