# Deployment Guide: Legal Advisory System v5.0

## 🚀 Deploy to Railway (Backend) + Netlify (Frontend)

This guide will walk you through deploying your Legal Advisory System to production.

---

## 📋 Prerequisites

Before you begin, you'll need:

1. **GitHub Account** (to host your code)
2. **Railway Account** (sign up at https://railway.app)
3. **Netlify Account** (sign up at https://netlify.com)
4. **Anthropic API Key** (get from https://console.anthropic.com/)

---

## Part 1: Deploy Backend to Railway

### Step 1: Push Your Code to GitHub

```bash
# In your project directory
cd /home/claude/legal-advisory-v5

# Initialize git if not already done
git init
git add .
git commit -m "Ready for Railway deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/legal-advisory-v5.git
git branch -M main
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select your `legal-advisory-v5` repository
6. Railway will automatically detect the project

### Step 3: Configure Environment Variables

In Railway dashboard:

1. Click on your project
2. Go to **Variables** tab
3. Add these environment variables:

```bash
# Required: Your Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx

# Optional: Logging level
LOG_LEVEL=INFO

# Optional: CORS Origins (add your Netlify URL after frontend deployment)
CORS_ORIGINS=https://your-app.netlify.app,http://localhost:5173
```

### Step 4: Deploy & Get URL

1. Railway will automatically deploy
2. Wait 2-3 minutes for build
3. Copy your Railway URL: `https://your-app-name.up.railway.app`
4. Test: Visit `https://your-app-name.up.railway.app/health`

✅ **Backend deployed!**

---

## Part 2: Deploy Frontend to Netlify

### Step 1: Create Netlify Site

1. Go to https://app.netlify.com/
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **GitHub** → Select `legal-advisory-v5` repository

### Step 2: Configure Build

```
Base directory: frontend
Build command: npm install && npm run build
Publish directory: frontend/dist
```

### Step 3: Set Environment Variable

In Netlify → **Site settings** → **Environment variables**:

```bash
Key: VITE_API_URL
Value: https://your-app-name.up.railway.app  # Your Railway URL
```

### Step 4: Deploy & Update CORS

1. Click **"Deploy site"** (wait 1-2 min)
2. Copy your Netlify URL: `https://your-app.netlify.app`
3. Go back to Railway → **Variables** → Update `CORS_ORIGINS`:

```bash
CORS_ORIGINS=https://your-app.netlify.app,http://localhost:5173
```

✅ **Frontend deployed!**

---

## ✅ Quick Deployment Checklist

**Railway (Backend):**
- [ ] GitHub repo connected
- [ ] `ANTHROPIC_API_KEY` set
- [ ] Backend URL copied
- [ ] `/health` endpoint works

**Netlify (Frontend):**
- [ ] GitHub repo connected  
- [ ] `VITE_API_URL` set to Railway URL
- [ ] Frontend loads
- [ ] Can send test queries

**Final:**
- [ ] Railway `CORS_ORIGINS` includes Netlify URL
- [ ] Test full workflow with sample query

---

## 🧪 Test Your Deployment

Visit your Netlify URL and try:

```
Calculate costs for a High Court default judgment with $50,000
```

You should see accurate Order 21 cost calculations!

---

## 💰 Estimated Costs

- **Railway**: $5/month (Starter)
- **Netlify**: Free tier OK for start
- **Anthropic API**: ~$0.003-0.006 per query
- **Total**: ~$10-15/month for hobby use

---

## 🐛 Troubleshooting

### "CORS Error"
→ Check Railway `CORS_ORIGINS` includes your Netlify URL

### "Cannot connect to API"
→ Verify `VITE_API_URL` in Netlify matches Railway URL

### "Mock mode" warning
→ Set `ANTHROPIC_API_KEY` in Railway environment variables

---

**Questions?** Check full docs or Railway/Netlify support.

*Legal Advisory System v5.0 - October 2025*
