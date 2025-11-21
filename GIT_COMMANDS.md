# Git Commands to Push Code to GitHub

Your GitHub repository is already connected: `https://github.com/YKap03/News-Sentiment-Driven-Stock-Explorer.git`

## Quick Commands

Run these commands in your project root directory:

```bash
# Navigate to project root (if not already there)
cd C:\Users\yash\OneDrive\Desktop\News-Sentiment-Driven-Stock-Explorer

# Add all files to staging
git add .

# Commit with a message
git commit -m "Initial commit: Ready for deployment on Render and Vercel"

# Push to GitHub
git push -u origin main
```

---

## Step-by-Step Breakdown

### 1. Make sure you're in the project root:
```bash
cd C:\Users\yash\OneDrive\Desktop\News-Sentiment-Driven-Stock-Explorer
```

### 2. Add all files to staging:
```bash
git add .
```
This stages all files (except those in `.gitignore`).

### 3. Commit your changes:
```bash
git commit -m "Your commit message here"
```
Replace with a meaningful message like:
- `"Initial commit: Ready for deployment"`
- `"Add deployment configuration and documentation"`
- `"Complete deployment setup for Render and Vercel"`

### 4. Push to GitHub:
```bash
git push -u origin main
```
- `-u` sets up tracking so future pushes can just be `git push`
- `origin` is your GitHub remote
- `main` is your branch name

---

## What Gets Pushed

✅ **Will be pushed:**
- All code files (`.py`, `.tsx`, `.ts`, `.json`, etc.)
- Configuration files (`requirements.txt`, `package.json`, `vite.config.ts`)
- Documentation (`.md` files)
- SQL migration scripts
- Everything not in `.gitignore`

❌ **Won't be pushed** (protected by `.gitignore`):
- `.env` files (your secrets!)
- `__pycache__/` folders
- `node_modules/` folder
- `.venv/` folder
- Local build artifacts

---

## Future Updates

After making changes, repeat steps 2-4:

```bash
git add .
git commit -m "Description of your changes"
git push
```

(You can use just `git push` after the first time since tracking is set up)

---

## Troubleshooting

**If you get "nothing to commit":**
- All files are already committed
- Check with `git status` to see if there are any uncommitted changes

**If you get "authentication failed":**
- You may need to use a personal access token instead of password
- Or use SSH instead of HTTPS
- GitHub: Settings → Developer settings → Personal access tokens → Generate new token

**If you get "remote rejected":**
- Someone else may have pushed to the repo
- Pull first: `git pull origin main --rebase`
- Then push again: `git push`

**If you want to see what will be committed:**
```bash
git status          # See what's staged/unstaged
git diff --staged   # See changes that will be committed
```

---

## Verify Your Push

After pushing, check your GitHub repository:
- Go to: https://github.com/YKap03/News-Sentiment-Driven-Stock-Explorer
- You should see all your files there

