# Railway Backend Deployment Guide
## Legal Advisory System v5.0

**Platform:** Railway.app
**Deployment Time:** ~5 minutes
**Cost:** Free tier available (500 hours/month)

---

## Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app)
- Git repository with your code

---

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

**1.1: Ensure all files are committed**

```bash
cd /home/claude/legal-advisory-v5

# Check status
git status

# Commit any changes
git add .
git commit -m "Prepare for Railway deployment"

# Push to GitHub
git push origin main
```

**1.2: Verify required files exist**

✅ `Dockerfile` - Present
✅ `requirements.txt` - Present
✅ `.env.example` - Present
✅ Railway will auto-detect these

---

### Step 2: Create Railway Account

**2.1: Sign up**
1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your repositories

**2.2: Verify account**
- Email verification may be required
- Free tier: 500 hours/month, $5 credit

---

### Step 3: Create New Project

**3.1: From Railway Dashboard**
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `legal-advisory-v5`
4. Click **"Deploy Now"**

**3.2: Railway Auto-Detection**
Railway will automatically:
- ✅ Detect `Dockerfile`
- ✅ Build Docker image
- ✅ Deploy to Railway infrastructure

---

### Step 4: Configure Environment Variables

**4.1: Navigate to Variables**
1. Click on your deployed service
2. Go to **"Variables"** tab
3. Click **"Add Variable"**

**4.2: Add Required Variables**

**Essential:**
```bash
PYTHONPATH=/app
ENVIRONMENT=production
PORT=8000
LOG_LEVEL=info
```

**For AI Features (Optional):**
```bash
ANTHROPIC_API_KEY=your-api-key-here
```

**For Security (Recommended):**
```bash
SECRET_KEY=your-generated-secret-key
CORS_ORIGINS=https://your-frontend.netlify.app
```

**4.3: Generate Secret Key**
```bash
# Run locally to generate
openssl rand -hex 32

# Copy the output and add as SECRET_KEY
```

---

### Step 5: Configure Domain & Networking

**5.1: Get Railway Domain**
1. Go to **"Settings"** tab
2. Under **"Domains"**
3. Click **"Generate Domain"**
4. You'll get: `your-app.railway.app`

**5.2: (Optional) Add Custom Domain**
1. Click **"Custom Domain"**
2. Enter your domain: `api.yourdomain.com`
3. Add CNAME record to your DNS:
   ```
   Type: CNAME
   Name: api
   Value: your-app.railway.app
   ```

---

### Step 6: Verify Deployment

**6.1: Check Build Logs**
1. Go to **"Deployments"** tab
2. Click on latest deployment
3. View build logs
4. Wait for "Build Successful" ✅

**6.2: Test Health Endpoint**

```bash
# Replace with your Railway domain
curl https://your-app.railway.app/health

# Expected response:
{"status":"healthy"}
```

**6.3: Test API Documentation**

Open in browser:
```
https://your-app.railway.app/docs
```

You should see Swagger UI ✅

---

### Step 7: Test API Endpoints

**7.1: Create Session**

```bash
curl -X POST https://your-app.railway.app/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'

# Save the session_id from response
```

**7.2: Send Message**

```bash
curl -X POST https://your-app.railway.app/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_FROM_ABOVE",
    "message": "I need costs for a High Court default judgment for $50,000"
  }'
```

---

## Railway Configuration Tips

### Optimizing for Railway

**1. Set Resource Limits (Settings → Resources)**
- Memory: 512MB (sufficient for our app)
- CPU: Shared (default)

**2. Enable Auto-Deploy**
- Settings → Enable "Auto-Deploy"
- Every push to `main` triggers deployment

**3. Configure Health Checks**
Railway automatically uses `/health` endpoint

**4. View Logs**
- Click "View Logs" in dashboard
- Real-time application logs
- Filter by severity

---

## Environment Variables Reference

**Copy these to Railway Variables tab:**

```bash
# Required
PYTHONPATH=/app
ENVIRONMENT=production
PORT=8000

# Logging
LOG_LEVEL=info

# CORS (Update with your Netlify URL)
CORS_ORIGINS=https://your-frontend.netlify.app,https://your-custom-domain.com

# Security
SECRET_KEY=your-secret-key-from-openssl

# AI Service (Optional - for AI features)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Feature Flags
ENABLE_AI=true
ENABLE_DOCS=true
DETAILED_ERRORS=false
```

---

## Common Issues & Solutions

### Issue 1: Build Fails

**Symptoms:** Build logs show errors

**Solutions:**
```bash
# Check Dockerfile syntax
docker build -t test .

# Verify requirements.txt
pip install -r requirements.txt

# Check for missing files
git ls-files
```

### Issue 2: App Crashes on Start

**Check Logs:**
1. Railway Dashboard → View Logs
2. Look for startup errors

**Common Causes:**
- Missing environment variables
- Port not set to 8000
- PYTHONPATH not set

**Fix:**
```bash
# Ensure these are set:
PYTHONPATH=/app
PORT=8000
```

### Issue 3: Health Check Fails

**Test Locally:**
```bash
docker run -p 8000:8000 your-image
curl localhost:8000/health
```

**Verify:**
- App is running on port 8000
- Health endpoint responds
- No errors in logs

### Issue 4: CORS Errors (when connecting frontend)

**Fix:**
1. Add your Netlify URL to CORS_ORIGINS:
```bash
CORS_ORIGINS=https://your-app.netlify.app
```

2. Redeploy

---

## Monitoring Your Railway Deployment

### 1. View Metrics
- Dashboard shows CPU, Memory, Network usage
- Monitor for spikes or issues

### 2. Set Up Alerts
- Railway can notify you of deployment failures
- Configure in Settings → Notifications

### 3. Check Logs Regularly
```bash
# Filter logs
- Click "View Logs"
- Filter by ERROR, WARN
- Monitor API calls
```

---

## Scaling on Railway

### Vertical Scaling
**Upgrade Resources:**
1. Settings → Service
2. Increase Memory/CPU
3. Cost increases with resources

### Horizontal Scaling
**Multiple Instances:**
- Available on paid plans
- Load balancing automatic
- Session state needs Redis (future)

---

## Cost Estimation

**Free Tier:**
- 500 hours/month
- $5 credit
- Suitable for development/testing

**Starter Plan ($5/month):**
- Unlimited hours
- Shared resources
- Good for small production

**Pro Plan ($20/month):**
- Dedicated resources
- Better performance
- Recommended for production

**Current App Usage:**
- ~2MB RAM (very light)
- Minimal CPU
- Should run comfortably on Free tier initially

---

## Your Railway Deployment URL

After deployment, you'll have:

**API Base URL:**
```
https://your-app.railway.app
```

**Health Check:**
```
https://your-app.railway.app/health
```

**API Documentation:**
```
https://your-app.railway.app/docs
```

**API Endpoints:**
```
POST https://your-app.railway.app/sessions
POST https://your-app.railway.app/messages
GET  https://your-app.railway.app/modules
GET  https://your-app.railway.app/statistics
```

---

## Next Steps

After Railway deployment:

1. ✅ Save your Railway URL
2. ✅ Test all endpoints
3. ✅ Configure CORS for frontend
4. ✅ Move to frontend deployment (Netlify)
5. ✅ Connect frontend to backend
6. ✅ Test end-to-end flow

---

## Quick Reference Card

```bash
# Railway CLI (optional)
npm i -g @railway/cli
railway login
railway link
railway up

# View logs
railway logs

# Environment variables
railway variables set KEY=VALUE

# Open dashboard
railway open
```

---

**Railway Deployment Complete! ✅**

Your backend is now live at: `https://your-app.railway.app`

Next: [Deploy Frontend to Netlify](NETLIFY_DEPLOYMENT.md)
