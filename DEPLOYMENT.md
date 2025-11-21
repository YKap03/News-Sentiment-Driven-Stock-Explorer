# Deployment Checklist

## Pre-Deployment

### Backend (Render)

- [ ] Create Supabase project and get `DATABASE_URL`
- [ ] Get API keys:
  - [ ] Finnhub API key
  - [ ] NewsAPI.org API key
  - [ ] OpenAI API key
- [ ] Test locally:
  - [ ] `python init_db.py` - creates tables
  - [ ] `python train_model.py` - trains model
  - [ ] `uvicorn app:app --reload` - starts API
- [ ] Commit all code to GitHub

### Frontend (Vercel)

- [ ] Test locally:
  - [ ] `npm install`
  - [ ] `npm run dev` - starts dev server
  - [ ] `npm run build` - builds for production
- [ ] Commit all code to GitHub

## Deployment Steps

### 1. Deploy Backend to Render

1. Go to https://render.com
2. Create new **Web Service**
3. Connect GitHub repository
4. Configure:
   - **Name**: `news-stock-backend` (or your choice)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL`
   - `FINNHUB_API_KEY`
   - `NEWSAPI_API_KEY`
   - `OPENAI_API_KEY`
6. Deploy
7. **After first deployment**, SSH into instance and run:
   ```bash
   cd backend
   python init_db.py
   python train_model.py
   ```
8. Note the backend URL (e.g., `https://news-stock-backend.onrender.com`)

### 2. Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Import GitHub repository
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variable:
   - `VITE_API_BASE_URL`: Your Render backend URL
5. Deploy
6. Note the frontend URL

## Post-Deployment

- [ ] Test backend endpoints:
  - [ ] `GET /api/tickers`
  - [ ] `GET /api/model-metrics`
- [ ] Test frontend:
  - [ ] Loads correctly
  - [ ] Can select ticker
  - [ ] Can fetch analysis
- [ ] Monitor API usage:
  - [ ] Check Finnhub rate limits
  - [ ] Check NewsAPI rate limits
  - [ ] Monitor OpenAI costs

## Troubleshooting

**Backend won't start:**
- Check environment variables are set
- Check logs in Render dashboard
- Verify database connection

**Frontend can't connect to backend:**
- Verify `VITE_API_BASE_URL` is correct
- Check CORS settings in `backend/app.py`
- Test backend URL directly in browser

**Model not found:**
- SSH into Render instance
- Run `python train_model.py` in backend directory
- Verify `models/classifier.pkl` exists

**Database errors:**
- Verify Supabase project is active
- Check connection string format
- Ensure tables exist (run `init_db.py`)

## Environment Variables Reference

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:port/database
FINNHUB_API_KEY=your_key
NEWSAPI_API_KEY=your_key
OPENAI_API_KEY=your_key
```

### Frontend (.env.local)
```env
VITE_API_BASE_URL=https://your-backend.onrender.com
```

