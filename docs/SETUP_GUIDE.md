# Setup Guide

## Prerequisites

- **Python 3.11+**: Download from [python.org](https://www.python.org/downloads/)
- **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
- **OpenAI API Key**: Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Git**: Download from [git-scm.com](https://git-scm.com/)

## Local Development Setup

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` file** with your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   DEBUG=false
   FRONTEND_URL=http://localhost:3000
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```
   Server will be available at `http://localhost:8000`

7. **Test the health endpoint**:
   ```bash
   curl http://localhost:8000/health
   # Response: {"status":"ok"}
   ```

### Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Copy environment template**:
   ```bash
   cp .env.local.example .env.local
   ```

3. **Edit `.env.local`** (should match backend URL):
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
   ```

4. **Install dependencies**:
   ```bash
   npm install
   ```

5. **Run development server**:
   ```bash
   npm run dev
   ```
   Application will be available at `http://localhost:3000`

## Local Testing Checklist

- [ ] Backend server starts without errors
- [ ] Frontend dev server starts without errors
- [ ] Chat interface loads at localhost:3000
- [ ] Can send a message and receive a response
- [ ] Language selector changes response language
- [ ] Message timestamps are displayed correctly
- [ ] Auto-scroll works when new messages arrive
- [ ] "Thinking..." indicator appears during response generation

## Production Deployment

### Railway Backend Deployment

1. **Connect Railway to GitHub**:
   - Log in to [railway.app](https://railway.app/)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `lenoir-nguyen/lenoir-chatbot`

2. **Configure environment variables**:
   - In Railway project settings, add:
     ```
     OPENAI_API_KEY=sk-proj-your-key
     DEBUG=false
     FRONTEND_URL=https://your-vercel-domain.vercel.app
     ```

3. **Deploy**:
   - Railway auto-deploys on push to main branch
   - Monitor logs in Railway dashboard

4. **Get Railway URL**:
   - From Railway project, copy the generated URL (e.g., `https://lenoir-chatbot-production.up.railway.app`)

### Vercel Frontend Deployment

1. **Connect Vercel to GitHub**:
   - Log in to [vercel.com](https://vercel.com/)
   - Click "New Project" → "Import Git Repository"
   - Select `lenoir-nguyen/lenoir-chatbot`
   - Select "Frontend" as root directory

2. **Configure environment variables**:
   - In Vercel project settings, add:
     ```
     NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
     NEXT_PUBLIC_FRONTEND_URL=https://your-vercel-domain.vercel.app
     ```

3. **Deploy**:
   - Vercel auto-deploys on push to main branch
   - Monitor build logs in Vercel dashboard

4. **Update Railway config**:
   - After Vercel deployment URL is known, update `FRONTEND_URL` in Railway environment variables

## Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```bash
uvicorn main:app --reload --port 8001
```

**ModuleNotFoundError: No module named 'fastapi'**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

**OpenAI API key error**:
- Verify key is correct in `.env`
- Check key is active at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Frontend Issues

**Port 3000 already in use**:
```bash
npm run dev -- -p 3001
```

**CORS error when sending messages**:
- Verify backend is running at correct URL in `.env.local`
- Check `FRONTEND_URL` in backend `.env` matches frontend URL

**TypeScript errors**:
```bash
npm run build
```
This will show all type issues before deploying.

### General Issues

**Dependency conflicts**:
```bash
# Backend
pip install --upgrade pip
rm -rf venv && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

**Git authentication fails on Railway**:
- Check GitHub personal access token is set in Railway project settings
- Verify token has `repo` and `workflow` permissions

---
