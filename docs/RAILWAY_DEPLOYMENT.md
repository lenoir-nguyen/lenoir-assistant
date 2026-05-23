# Railway Deployment Guide - Lenoir Chatbot v4

**Target:** Production deployment with PostgreSQL, Redis, FastAPI backend, and Next.js frontend

---

## Prerequisites

✅ Local v4 implementation complete and tested  
✅ PIN authentication working  
✅ Chat history persistence verified  
✅ All features tested locally  

**Before starting:**
- Railway account created: https://railway.app
- GitHub repo connected to Railway (recommended for auto-deploy)
- Both backend and frontend ready to deploy

---

## Step 1: Create Railway Project

### 1.1 Create New Project
```
1. Log into railway.app
2. Click "Create New Project"
3. Select "Deploy from GitHub" (recommended) OR "Blank Project"
4. If GitHub: authorize and select lenoir-chatbot repo
```

### 1.2 Add PostgreSQL Database
```
1. In Railway project, click "Add Service"
2. Select "Database" → "PostgreSQL"
3. Railway auto-generates:
   - DATABASE_URL (connection string)
   - PGPASSWORD
   - PGUSER
4. Save these values - we'll use them in environment variables
```

### 1.3 Add Redis Cache
```
1. Click "Add Service" again
2. Select "Redis"
3. Railway auto-generates:
   - REDIS_URL (connection string)
4. Save this value
```

---

## Step 2: Configure Environment Variables

### 2.1 Backend Environment Variables

In Railway Dashboard → Your Project → Backend Service → Variables:

```
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-<your-key-here>

# Server
DEBUG=false
FRONTEND_URL=<your-vercel-frontend-url>  # Will update after frontend deploy

# Authentication (v4+)
OWNER_API_KEY_HASH=888df25ae35772424a560c7152a1de794440e0ea5cfee62828333a456a506e05

# Auth Token TTL
AUTH_TOKEN_TTL=86400

# Database (PostgreSQL)
DATABASE_URL=<railway-postgres-url>  # Auto-provided by Railway PostgreSQL addon
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_ECHO=false

# Cache (Redis)
REDIS_URL=<railway-redis-url>  # Auto-provided by Railway Redis addon
```

### 2.2 Frontend Environment Variables

In Railway Dashboard → Your Project → Frontend Service → Variables:

```
NEXT_PUBLIC_API_URL=https://<backend-domain>.railway.app
```

---

## Step 3: Deploy Backend (FastAPI)

### Option A: Deploy from GitHub (Recommended)

```
1. In Railway Project → "Add Service" → "GitHub Repo"
2. Select "lenoir-chatbot" repo
3. Railway auto-detects: Backend at ./backend/
4. Select root directory: /backend
5. Select build command: (leave default or select python)
6. Click "Deploy"
```

### Option B: Deploy Manually

```
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# In backend directory
cd backend
railway init
railway variables set DATABASE_URL="<your-postgres-url>"
railway variables set REDIS_URL="<your-redis-url>"
railway variables set OPENAI_API_KEY="sk-proj-..."
railway deploy
```

### 3.1 Run Migrations

After backend deployment, run Alembic migrations:

```bash
# Via Railway CLI
railway run alembic upgrade head

# OR via SSH into deployed backend
ssh <railway-backend-container>
cd /app
alembic upgrade head
```

**Verify migration worked:**
```bash
# Check if tables were created
railway run psql -c "\dt"  # Should show sessions, messages tables
```

---

## Step 4: Deploy Frontend (Next.js)

### Option A: Deploy to Vercel (Recommended)

Vercel is optimized for Next.js:

```
1. Go to vercel.com
2. Click "Import Project"
3. Select GitHub repo (lenoir-chatbot)
4. Framework: Next.js (auto-detected)
5. Root directory: ./frontend
6. Environment variables:
   NEXT_PUBLIC_API_URL=https://<backend-domain>.railway.app
7. Click "Deploy"
```

**Update backend FRONTEND_URL:**
```
After Vercel deploy, you'll have: https://<your-project>.vercel.app

Go back to Railway → Backend Variables
Update: FRONTEND_URL=https://<your-project>.vercel.app
```

### Option B: Deploy on Railway

```
# In Railway project, add frontend service
1. "Add Service" → GitHub Repo
2. Select lenoir-chatbot
3. Root directory: /frontend
4. Build command: npm run build
5. Start command: npm start
6. Set NEXT_PUBLIC_API_URL to Railway backend URL
7. Deploy
```

---

## Step 5: Verify Production Deployment

### 5.1 Health Check

```bash
# Test backend health
curl https://<backend-domain>.railway.app/health

# Expected response:
{
  "status": "ok",
  "redis": "connected",
  "database": "connected"
}
```

### 5.2 Test Frontend

```
1. Visit: https://<frontend-domain>.vercel.app (or railway.app)
2. Should load auth screen
3. Login as owner with PIN: 9999
4. Send test message
5. Verify message appears
6. Refresh page
7. Verify chat history persists (shows previous messages)
```

### 5.3 Test Chat Persistence

```bash
# Log in as owner
POST https://<backend>/auth/login
{
  "passphrase": "9999",
  "pin": ""
}

# Send message
POST https://<backend>/chat/message
Authorization: Bearer <token-from-login>
{
  "message": "Hello from production!",
  "language": "en",
  "session_id": null
}

# Get chat history
GET https://<backend>/chat/history/<session-id-from-response>
Authorization: Bearer <token>

# Should return: [{"role": "user", "content": "Hello..."}, {"role": "assistant", "content": "..."}]
```

---

## Step 6: Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
# Via Railway CLI
railway logs

# Look for:
- Database connection errors → Check DATABASE_URL
- Redis connection errors → Check REDIS_URL
- Migration errors → Run: railway run alembic upgrade head
- Missing env vars → Check all required vars are set
```

### Frontend Can't Reach Backend

```
1. Check NEXT_PUBLIC_API_URL is correct
2. Verify backend health endpoint works
3. Check CORS settings in FastAPI (should allow frontend URL)
```

### Chat Messages Not Persisting

```bash
# Check database tables exist
railway run psql -c "\dt"

# Check messages table has data
railway run psql -c "SELECT COUNT(*) FROM messages;"

# Check sessions table
railway run psql -c "SELECT * FROM sessions LIMIT 5;"
```

### Authentication Failing

```
1. Verify OWNER_API_KEY_HASH is set in Railway variables
2. Verify hash is correct: sha256('9999') = 888df25ae35772424a560c7152a1de794440e0ea5cfee62828333a456a506e05
3. Check backend logs for auth errors
```

---

## Step 7: Post-Deployment

### 7.1 Monitor in Production

```bash
# Watch backend logs
railway logs --follow

# Check service health
railway status
```

### 7.2 Update DNS (Optional)

If using custom domain:
```
CNAME record → <railway-backend>.railway.app
```

### 7.3 Enable HTTPS

Railway provides free HTTPS automatically for *.railway.app domains

For custom domain:
```
1. Go to Railway project settings
2. Domains → Add custom domain
3. Add CNAME record in your DNS
4. Railway auto-provisions SSL certificate
```

---

## Step 8: Rollback / Troubleshooting

### If Deployment Fails

```bash
# View Railway build logs
railway logs --build

# Redeploy specific service
railway redeploy

# Rollback to previous deployment
railway rollback
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Database connection timeout | Increase DATABASE_POOL_SIZE, check REDIS_URL |
| 502 Bad Gateway | Check backend logs, verify health endpoint |
| Chat history not loading | Run migrations: `railway run alembic upgrade head` |
| File uploads failing | Check storage, use Railway volumes |

---

## Final Checklist

Before going live:

- [ ] PostgreSQL database created and tested
- [ ] Redis cache created and tested
- [ ] Backend environment variables set
- [ ] Backend deployed and health check passing
- [ ] Frontend environment variables set
- [ ] Frontend deployed and loads correctly
- [ ] Alembic migrations run successfully
- [ ] Owner login works with PIN 9999
- [ ] Chat messages persist after refresh
- [ ] Guest mode works (ephemeral)
- [ ] Clear button works
- [ ] Logout button works
- [ ] Record button works (voice)
- [ ] No error messages in production logs

---

## Next Steps

1. Create Railway project and addons
2. Configure environment variables
3. Deploy backend from GitHub
4. Deploy frontend to Vercel
5. Run migrations
6. Test all features in production
7. Monitor logs for errors

Good luck! 🚀
