# Quick Deployment Checklist

Use this alongside `DEPLOYMENT_STEPS.md` to track your progress.

---

## ✅ Account Setup

- [ ] **Alpha Vantage API Key**
  - [ ] Signed up at https://www.alphavantage.co/support/#api-key
  - [ ] Saved API key: `________________________`

- [ ] **OpenAI API Key** (Optional)
  - [ ] Created key at https://platform.openai.com/api-keys
  - [ ] Saved API key: `sk-________________________`

- [ ] **Supabase Account**
  - [ ] Created project at https://supabase.com
  - [ ] Project URL: `https://________________.supabase.co`
  - [ ] Anon key: `eyJ________________________`
  - [ ] Ran `init_supabase_tables.sql` in SQL Editor
  - [ ] Ran migration scripts (if any)

- [ ] **Render Account**
  - [ ] Signed up at https://render.com
  - [ ] Connected GitHub account

- [ ] **Vercel Account**
  - [ ] Signed up at https://vercel.com
  - [ ] Connected GitHub account

---

## ✅ Backend Deployment (Render)

- [ ] Created Web Service on Render
  - [ ] Root directory: `backend`
  - [ ] Build command: `pip install -r requirements.txt`
  - [ ] Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

- [ ] Set Environment Variables in Render:
  - [ ] `SUPABASE_URL` = `https://________________.supabase.co`
  - [ ] `SUPABASE_KEY` = `eyJ________________________`
  - [ ] `ALPHAVANTAGE_API_KEY` = `________________________`
  - [ ] `OPENAI_API_KEY` = `sk-________________________` (optional)
  - [ ] `ALLOWED_ORIGINS` = (leave blank or set to `https://*.vercel.app`)

- [ ] Backend deployed successfully
  - [ ] Backend URL: `https://________________.onrender.com`
  - [ ] Health check works: `/health` returns `{"status":"ok"}`
  - [ ] Root endpoint works: `/` returns API message

- [ ] Database initialized
  - [ ] Ran `python init_db.py` (creates tickers)
  - [ ] Ran `python train_model.py` (trains ML model)

---

## ✅ Frontend Deployment (Vercel)

- [ ] Imported project to Vercel
  - [ ] Root directory: `frontend`
  - [ ] Build command: `npm run build` (auto-detected)
  - [ ] Output directory: `dist` (auto-detected)

- [ ] Set Environment Variable in Vercel:
  - [ ] `VITE_API_BASE_URL` = `https://________________.onrender.com`

- [ ] Frontend deployed successfully
  - [ ] Frontend URL: `https://________________.vercel.app`

- [ ] Updated Backend CORS (if needed)
  - [ ] Set `ALLOWED_ORIGINS` in Render to your Vercel URL

---

## ✅ Testing

- [ ] Frontend loads at Vercel URL
- [ ] Can select tickers from dropdown
- [ ] Can select date range
- [ ] API calls work (check browser DevTools → Network)
- [ ] Data displays correctly (prices, sentiment, articles)
- [ ] No CORS errors in browser console
- [ ] No errors in browser console

---

## 📝 Your Deployment URLs

**Frontend (Share this with users):**
```
https://________________.vercel.app
```

**Backend API:**
```
https://________________.onrender.com
```

**Health Check:**
```
https://________________.onrender.com/health
```

---

## 🆘 If Something Goes Wrong

1. **Check Render logs**: Render dashboard → Your service → Logs tab
2. **Check Vercel logs**: Vercel dashboard → Your project → Deployments → Click deployment → View build logs
3. **Check browser console**: F12 → Console tab for frontend errors
4. **Check Network tab**: F12 → Network tab to see API calls
5. **Verify environment variables**: Make sure all are set correctly in Render and Vercel
6. **Test backend directly**: Visit backend URL + `/health` to verify it's running

---

**Once all checkboxes are checked, your app is live! 🎉**

