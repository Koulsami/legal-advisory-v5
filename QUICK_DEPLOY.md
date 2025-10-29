# Quick Deploy Reference Card

## 🚀 Railway Backend (5 minutes)

```bash
# 1. Push to GitHub
git push origin main

# 2. Railway Dashboard
- New Project → GitHub repo
- Variables → Add:
  ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
  CORS_ORIGINS=https://your-app.netlify.app

# 3. Copy URL
https://your-app-name.up.railway.app
```

---

## 🌐 Netlify Frontend (3 minutes)

```bash
# 1. Netlify Dashboard
- New site → GitHub repo
- Base: frontend
- Build: npm install && npm run build
- Publish: frontend/dist

# 2. Environment Variables
VITE_API_URL=https://your-app-name.up.railway.app

# 3. Update Railway CORS
Add your Netlify URL to Railway CORS_ORIGINS
```

---

## ✅ Test

```
https://your-app.netlify.app
→ "Calculate costs for High Court default judgment with $50,000"
→ Should see: $4,000 calculation
```

Done! 🎉
