# ⚡ Quick Start Reference

## Required Accounts & API Keys

| Service | URL | Free Tier? | What You Need |
|---------|-----|------------|---------------|
| **Supabase** | https://supabase.com | ✅ Yes | Connection string (from Settings → Database) |
| **Finnhub** | https://finnhub.io | ✅ Yes | API Key (from dashboard) |
| **NewsAPI.org** | https://newsapi.org | ✅ Yes | API Key (from API Keys section) |
| **OpenAI** | https://platform.openai.com | ❌ Pay-per-use | API Key (from API Keys section) |

## File Locations

### Backend `.env` file
**Location:** `backend/.env`

**Content:**
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
FINNHUB_API_KEY=your_finnhub_key
NEWSAPI_API_KEY=your_newsapi_key
OPENAI_API_KEY=sk-your_openai_key
```

### Frontend `.env.local` file
**Location:** `frontend/.env.local`

**Content:**
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Setup Commands

```bash
# 1. Backend setup
cd backend
pip install -r requirements.txt

# 2. Initialize database
python init_db.py

# 3. Train ML model
python train_model.py

# 4. Start backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

```bash
# 5. Frontend setup (in new terminal)
cd frontend
npm install
npm run dev
```

## Quick Checklist

- [ ] Create Supabase project → Get connection string
- [ ] Sign up for Finnhub → Get API key
- [ ] Sign up for NewsAPI → Get API key
- [ ] Sign up for OpenAI → Get API key
- [ ] Create `backend/.env` with all keys
- [ ] Create `frontend/.env.local` with API URL
- [ ] Run `python init_db.py`
- [ ] Run `python train_model.py`
- [ ] Start backend: `uvicorn app:app --reload`
- [ ] Start frontend: `npm run dev`

## Where to Find Connection Strings/Keys

### Supabase Connection String
1. Go to your Supabase project
2. Settings (⚙️) → Database
3. Scroll to "Connection string"
4. Copy "URI" under "Connection pooling"
5. Replace `[YOUR-PASSWORD]` with your database password

### Finnhub API Key
1. Log in to https://finnhub.io
2. API key is displayed on dashboard
3. Copy it

### NewsAPI Key
1. Log in to https://newsapi.org
2. Go to "API Keys" section
3. Copy your key

### OpenAI API Key
1. Log in to https://platform.openai.com
2. Go to "API Keys" (left sidebar)
3. Click "Create new secret key"
4. Copy immediately (you won't see it again!)

---

📖 **For detailed instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

