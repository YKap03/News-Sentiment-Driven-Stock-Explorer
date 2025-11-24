# Database Initialization Guide for Render Deployment

## Overview

You need to create the database tables in Supabase first, then seed initial data. Here's how to do it:

---

## ✅ Step 1: Create Tables in Supabase SQL Editor

**Important:** You must do this FIRST before running `init_db.py`!

### 1.1 Go to Supabase SQL Editor

1. Open your Supabase project dashboard: https://supabase.com/dashboard
2. Click **"SQL Editor"** in the left sidebar
3. Click **"New query"**

### 1.2 Run the Main SQL Script

1. Open `backend/db/init_supabase_tables.sql` from your codebase
2. Copy **ALL** the SQL code from that file
3. Paste it into the Supabase SQL Editor
4. Click **"Run"** (or press Ctrl+Enter)

**Expected result:** You should see "Success. No rows returned" message.

### 1.3 Run Migration Scripts

Repeat the process for each migration file:

1. **`backend/db/migrate_add_is_relevant.sql`**
   - Copy all SQL from the file
   - Paste into SQL Editor
   - Click "Run"

2. **`backend/db/migrate_add_relevance_score.sql`**
   - Copy all SQL from the file
   - Paste into SQL Editor
   - Click "Run"

**✅ Tables Created!** Your database structure is now ready.

---

## ✅ Step 2: Seed Initial Data (Tickers)

Now you need to run `init_db.py` to add initial tickers (AAPL, MSFT, etc.). You have two options:

### Option A: Using Render Shell (Recommended)

**This uses the environment variables already set in Render.**

1. **Open Render Dashboard:**
   - Go to: https://dashboard.render.com
   - Select your service: **News-Sentiment-Driven-Stock-Explorer**

2. **Open Shell:**
   - Click **"Shell"** tab in the left sidebar
   - Click **"Connect"** button
   - Wait for the shell to connect (may take 10-20 seconds)

3. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

4. **Run initialization script:**
   ```bash
   python init_db.py
   ```

   **Expected output:**
   ```
   Initializing database with Supabase...
   
   NOTE: Make sure you've run the SQL script in Supabase SQL Editor first!
   The SQL script is located at: backend/db/init_supabase_tables.sql
   
   Added ticker: AAPL - Apple Inc.
   Added ticker: MSFT - Microsoft Corporation
   ...
   Tickers seeded successfully
   
   Database initialization complete!
   ```

5. **(Optional) Train the ML model:**
   ```bash
   python train_model.py
   ```
   (This may take a few minutes depending on data in your database)

**✅ Database Initialized!**

### Option B: Run Locally (Alternative)

If Render Shell doesn't work or you prefer to run locally:

1. **Create local `.env` file** in `backend/` directory:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key
   ALPHAVANTAGE_API_KEY=your-alpha-vantage-key
   OPENAI_API_KEY=your-openai-key
   ```
   (Use the same values from your Render environment variables)

2. **Navigate to backend and run:**
   ```bash
   cd backend
   python init_db.py
   ```

3. **(Optional) Train model:**
   ```bash
   python train_model.py
   ```

**✅ Database Initialized!**

---

## ✅ Step 3: Verify Database is Working

### Test from Render Shell:

```bash
python -c "from db import crud_supabase; print(crud_supabase.get_tickers())"
```

Should output a list of tickers like:
```
[{'id': 1, 'symbol': 'AAPL', 'name': 'Apple Inc.'}, ...]
```

### Test via API:

1. Make sure your Render service is running (check the "Logs" tab)
2. Visit: `https://your-service.onrender.com/api/tickers`
3. You should see JSON with tickers:
   ```json
   [
     {"symbol": "AAPL", "name": "Apple Inc."},
     ...
   ]
   ```

---

## 🆘 Troubleshooting

### Error: "Table doesn't exist"
**Solution:** You haven't run the SQL scripts yet. Go back to Step 1.

### Error: "Row Level Security policy violation"
**Solution:** 
- The SQL script should create policies automatically
- If not, go to Supabase → Authentication → Policies
- Or disable RLS temporarily: `ALTER TABLE tablename DISABLE ROW LEVEL SECURITY;`

### Error: "SUPABASE_URL not set"
**Solution:** Check that environment variables are set correctly in Render dashboard → Environment tab

### Shell won't connect
**Solution:** 
- Make sure your service is running (not sleeping)
- Try refreshing the page
- Wait a bit longer (sometimes takes 30 seconds)
- Use Option B (run locally) instead

---

## 📝 Summary Checklist

- [ ] Step 1: Created tables in Supabase SQL Editor
  - [ ] Ran `init_supabase_tables.sql`
  - [ ] Ran `migrate_add_is_relevant.sql`
  - [ ] Ran `migrate_add_relevance_score.sql`

- [ ] Step 2: Initialized database
  - [ ] Ran `python init_db.py` (via Render Shell OR locally)
  - [ ] Tickers were added successfully

- [ ] Step 3: (Optional) Trained model
  - [ ] Ran `python train_model.py`
  - [ ] Model saved to `backend/models/classifier.pkl`

- [ ] Step 4: Verified
  - [ ] Can access `/api/tickers` endpoint
  - [ ] Can fetch data for a ticker

---

**Once complete, your database is ready and your app should work!** 🎉

