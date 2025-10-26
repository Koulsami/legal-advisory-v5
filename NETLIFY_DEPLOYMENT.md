# Netlify Frontend Deployment Guide
## Legal Advisory System v5.0

**Platform:** Netlify
**Deployment Time:** ~3 minutes
**Cost:** Free tier available (100 GB bandwidth/month)

---

## Prerequisites

- GitHub account with frontend code
- Netlify account (sign up at https://netlify.com)
- Railway backend already deployed (see [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md))

---

## Step-by-Step Deployment

### Step 1: Prepare Frontend Code

**1.1: Commit frontend to repository**

```bash
cd /home/claude/legal-advisory-v5

# Add frontend files
git add frontend/
git commit -m "Add React frontend for Netlify deployment"
git push origin main
```

**1.2: Verify frontend structure**

```
frontend/
├── src/
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── public/
├── index.html
├── package.json
├── vite.config.js
├── netlify.toml
└── .env.example
```

---

### Step 2: Create Netlify Account

**2.1: Sign up**
1. Go to https://netlify.com
2. Click **"Sign up"**
3. Choose **"Sign up with GitHub"**
4. Authorize Netlify to access repositories

**2.2: Verify account**
- Free tier: 100 GB bandwidth, 300 build minutes
- No credit card required for free tier

---

### Step 3: Create New Site

**3.1: From Netlify Dashboard**
1. Click **"Add new site"** → **"Import an existing project"**
2. Choose **"Deploy with GitHub"**
3. Select your repository: `legal-advisory-v5`
4. Authorize access if prompted

---

### Step 4: Configure Build Settings

**4.1: Build Settings**

Fill in these values:

```
Base directory: frontend

Build command: npm run build

Publish directory: frontend/dist

Branch to deploy: main
```

**4.2: Environment Variables**

Click **"Advanced build settings"** → **"New variable"**

Add this variable:

```
Key: VITE_API_URL
Value: https://your-app.railway.app
```

**Important:** Replace `your-app.railway.app` with your actual Railway backend URL!

---

### Step 5: Deploy

**5.1: Start Deployment**
1. Click **"Deploy site"**
2. Wait for build to complete (~1-2 minutes)
3. Watch build logs in real-time

**5.2: Build Process**
- Netlify clones your repository
- Installs dependencies (`npm install`)
- Runs build command (`npm run build`)
- Publishes `dist` folder

---

### Step 6: Get Your Site URL

**6.1: Temporary URL**
After deployment, you'll get:
```
https://random-name-12345.netlify.app
```

**6.2: Customize Site Name**
1. Go to **"Site settings"** → **"Site details"**
2. Click **"Change site name"**
3. Enter: `legal-advisory-app` (or your preferred name)
4. Your URL becomes:
```
https://legal-advisory-app.netlify.app
```

---

### Step 7: Update Backend CORS

**7.1: Add Netlify URL to Railway**

1. Go to Railway dashboard
2. Select your API service
3. Go to **"Variables"**
4. Update `CORS_ORIGINS`:

```
CORS_ORIGINS=https://legal-advisory-app.netlify.app
```

5. Redeploy backend (Railway will auto-redeploy on variable change)

---

### Step 8: Test Your Deployment

**8.1: Open Your Site**

Visit: `https://legal-advisory-app.netlify.app`

**8.2: Verify Connection**
- Check status indicator (should show "Connected")
- Session should auto-create
- Try sending a test message

**8.3: Test Full Flow**

```
1. Open site
2. Wait for "Connected" status
3. Type: "I need costs for High Court default judgment $50,000"
4. Click Send
5. Verify calculation appears
```

---

## Configure Custom Domain (Optional)

### Step 1: Add Domain

1. Go to **"Domain settings"**
2. Click **"Add custom domain"**
3. Enter your domain: `legal.yourdomain.com`

### Step 2: Configure DNS

Add these records to your DNS provider:

```
Type: CNAME
Name: legal
Value: legal-advisory-app.netlify.app
TTL: 3600
```

### Step 3: Enable HTTPS

Netlify automatically provides SSL certificate via Let's Encrypt:
- Wait 24-48 hours for DNS propagation
- SSL will auto-configure
- Your site: `https://legal.yourdomain.com`

---

## Netlify Configuration Tips

### Enable Automatic Deploys

**Settings → Build & deploy → Continuous Deployment**

✅ Enable: **"Auto publishing"**
- Every push to `main` triggers build
- Preview deployments for pull requests

### Set up Deploy Notifications

**Settings → Build & deploy → Deploy notifications**

Add notifications for:
- Deploy started
- Deploy succeeded
- Deploy failed

Options:
- Email
- Slack
- Discord
- Webhook

### Configure Build Settings

**Build & deploy → Environment**

Recommended settings:

```
NODE_VERSION=18
NPM_FLAGS=--legacy-peer-deps  # if needed
```

---

## Troubleshooting

### Issue 1: Build Fails

**Check build logs:**
1. Deployments → Select failed deployment
2. Review logs

**Common causes:**
```bash
# Missing dependencies
Solution: Check package.json

# Wrong Node version
Solution: Add NODE_VERSION=18 to environment

# Build command error
Solution: Verify build command is "npm run build"
```

### Issue 2: Blank Page

**Symptoms:** Site loads but shows blank page

**Solutions:**

1. **Check browser console for errors**
```javascript
// Look for CORS errors
// Look for API connection errors
```

2. **Verify VITE_API_URL**
```bash
# In Netlify: Site settings → Environment variables
# Should be: https://your-app.railway.app
```

3. **Check backend is running**
```bash
curl https://your-app.railway.app/health
```

### Issue 3: Cannot Connect to API

**Symptoms:** "Disconnected" status

**Solutions:**

1. **Verify API URL in Netlify**
- Settings → Environment variables
- VITE_API_URL should match your Railway URL

2. **Check CORS on backend**
- Railway → Variables → CORS_ORIGINS
- Should include your Netlify URL

3. **Test backend directly**
```bash
curl https://your-app.railway.app/health
```

### Issue 4: Deployment Takes Too Long

**Normal build time:** 1-3 minutes

**If longer:**
- Check build logs for stuck processes
- Verify npm install completes
- Check for network issues

---

## Environment Variables Reference

**Required:**

```bash
VITE_API_URL=https://your-app.railway.app
```

**For staging environment:**

```bash
VITE_API_URL=https://your-staging-app.railway.app
```

---

## Deploy Commands Reference

### Using Netlify CLI (Optional)

**Install CLI:**
```bash
npm install -g netlify-cli
```

**Login:**
```bash
netlify login
```

**Deploy from terminal:**
```bash
cd frontend
netlify deploy

# Production deploy
netlify deploy --prod
```

**Link existing site:**
```bash
netlify link
```

---

## Monitoring Your Deployment

### Analytics

1. **Netlify Analytics** (optional, paid add-on)
- Real-time visitors
- Page views
- Bandwidth usage

2. **Google Analytics** (free)
- Add to index.html:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

### Bandwidth Monitoring

**Free tier limits:**
- 100 GB/month bandwidth
- 300 build minutes/month

**Check usage:**
- Dashboard → Team overview
- View current month usage

---

## Performance Optimization

### Enable Asset Optimization

**Build & deploy → Post processing**

Enable:
- ✅ Bundle CSS
- ✅ Minify CSS
- ✅ Minify JS
- ✅ Image optimization

### Configure Caching

Netlify automatically sets cache headers:
- Static assets: 1 year
- HTML: No cache (for updates)

### Add Headers (Optional)

Create `frontend/public/_headers`:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Cache-Control: public, max-age=31536000, immutable
```

---

## Your Complete Deployment URLs

After deployment, you'll have:

**Frontend (Netlify):**
```
https://legal-advisory-app.netlify.app
```

**Backend (Railway):**
```
https://your-app.railway.app
```

**API Endpoints:**
```
POST https://your-app.railway.app/sessions
POST https://your-app.railway.app/messages
GET  https://your-app.railway.app/modules
GET  https://your-app.railway.app/docs
```

---

## Deployment Checklist

After both deployments:

- [ ] Backend deployed on Railway ✅
- [ ] Backend health check passing
- [ ] Frontend deployed on Netlify ✅
- [ ] VITE_API_URL set correctly
- [ ] CORS configured on backend
- [ ] Frontend shows "Connected" status
- [ ] Can create session
- [ ] Can send messages
- [ ] Calculations display correctly
- [ ] (Optional) Custom domain configured
- [ ] (Optional) SSL certificate active

---

## Next Steps

1. ✅ Test complete user flow
2. ✅ Share links with stakeholders
3. ✅ Prepare customer demonstration
4. ✅ Monitor for errors
5. ✅ Gather feedback

---

**Frontend Deployment Complete! ✅**

Your application is now live:
- **Frontend:** `https://legal-advisory-app.netlify.app`
- **Backend:** `https://your-app.railway.app`

Next: [Customer Demonstration Guide](CUSTOMER_DEMO_GUIDE.md)
