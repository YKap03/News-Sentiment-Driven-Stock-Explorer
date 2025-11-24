# Initialize Database Locally (Without Render Shell)

Since Render Shell is not available on the free tier, you can run the database initialization **locally** - it will connect to the same Supabase database that your Render service uses.

---

## ✅ Step 1: Create Tables in Supabase (If Not Done)

1. Go to **Supabase Dashboard** → **SQL Editor**
2. Run `backend/db/init_supabase_tables.sql`
3. Run `backend/db/migrate_add_is_relevant.sql` (optional - safely skips if columns exist)

**✅ Tables created!**

---

## ✅ Step 2: Set Up Local Environment

### 2.1 Create `.env` file

1. Navigate to `backend/` folder on your local machine
2. Create a file named `.env` (not `.env.txt`, just `.env`)
3. Copy the values from your Render environment variables

**Get values from Render:**
- Go to Render dashboard → Your service → **Environment** tab
- Click the **eye icon** 👁️ next to each variable to reveal values
- Copy them to your local `.env` file

**Create `backend/.env`:**
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
ALPHAVANTAGE_API_KEY=your-alpha-vantage-key
OPENAI_API_KEY=your-openai-key
```

**⚠️ Important:** Use the exact same values from Render!

---

## ✅ Step 3: Run Initialization Locally

### 3.1 Make sure you have Python and dependencies

1. **Navigate to backend folder:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (if you don't have one):**
   ```bash
   python -m venv .venv
   ```
   
   **Activate it:**
   - **Windows PowerShell:**
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **Windows CMD:**
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **Mac/Linux:**
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3.2 Run initialization

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
Added ticker: GOOGL - Alphabet Inc.
...
Tickers seeded successfully

Database initialization complete!
```

### 3.3 (Optional) Train the model

```bash
python train_model.py
```

This trains the ML model on your data (may take a few minutes).

---

## ✅ Step 4: Verify It Worked

### Test from your local machine:

```bash
python -c "from db import crud_supabase; print(crud_supabase.get_tickers())"
```

Should show a list of tickers.

### Test via Render API:

Visit: `https://your-service.onrender.com/api/tickers`

Should return JSON with tickers:
```json
[
  {"symbol": "AAPL", "name": "Apple Inc."},
  {"symbol": "MSFT", "name": "Microsoft Corporation"},
  ...
]
```

---

## 🎯 Why This Works

- **Supabase is external:** It's a separate database service, not part of Render
- **Local script connects to same DB:** Your local `init_db.py` connects to the same Supabase database
- **Environment variables match:** Using same `SUPABASE_URL` and `SUPABASE_KEY` means you're working with the same database
- **No Render Shell needed:** Everything happens locally, just connecting to remote database

---

## 📝 Quick Commands Summary

```bash
# 1. Navigate to backend
cd backend

# 2. Create/activate virtual environment (if needed)
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. Install dependencies (if not already installed)
pip install -r requirements.txt

# 4. Make sure .env file exists with Supabase credentials

# 5. Run initialization
python init_db.py

# 6. (Optional) Train model
python train_model.py
```

---

## 🆘 Troubleshooting

**Error: "SUPABASE_URL not set"**
- Make sure `.env` file is in `backend/` directory
- Make sure file is named exactly `.env` (not `.env.txt`)
- Check that values match Render environment variables exactly

**Error: "Table doesn't exist"**
- Go back to Step 1 - run the SQL scripts in Supabase SQL Editor first

**Error: "No module named 'xxx'"**
- Run `pip install -r requirements.txt` to install dependencies

**Connection errors:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check Supabase dashboard to make sure project is active

---

**That's it! Your database will be initialized and your Render service can use it immediately.** 🎉

