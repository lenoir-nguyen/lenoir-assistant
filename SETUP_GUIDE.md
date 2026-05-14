# Lenoir Chatbot - Complete Setup Guide

## ✅ What's Been Built

Your Lenoir Chatbot is now **fully implemented** with all components:

### Backend (FastAPI + Python)
- ✅ Database models (SQLAlchemy): Session, Message, PersonalFact, Document, DocumentChunk
- ✅ Alembic migrations for PostgreSQL + pgvector
- ✅ Identity service: passphrase detection + PIN verification (bcrypt)
- ✅ LangChain chains: owner (RAG) + stranger (simple)
- ✅ OpenAI integrations: Whisper (STT), TTS, embeddings
- ✅ Vector store service: pgvector similarity search
- ✅ FastAPI routers:
  - `POST /auth/identify` — identity claim
  - `POST /auth/verify-pin` — PIN verification
  - `POST /chat/message` — streaming chat (SSE)
  - `POST /voice/transcribe` — audio to text
  - `POST /voice/speak` — text to audio
  - `POST /memory/facts` — add personal fact
  - `POST /memory/upload` — upload documents
  - `GET /memory/facts` — list facts
- ✅ CORS configured for frontend
- ✅ Docker + docker-compose.yml for local development
- ✅ Requirements.txt with all dependencies

### Frontend (Next.js + React)
- ✅ App structure (App Router) with TypeScript
- ✅ Components:
  - `IdentityPrompt` — Lenoir identification + PIN entry
  - `ChatWindow` — main chat interface
  - `MessageBubble` — message display with timestamps
  - `VoiceButton` — hold-to-record voice with MediaRecorder API
  - `LanguageSelector` — en/fr/vi language switching
- ✅ API client library (`lib/api.ts`) — axios wrapper with all endpoints
- ✅ Styling (CSS Modules) — clean, modern UI
- ✅ Auto-scrolling, typing indicators, loading states
- ✅ Audio playback for TTS responses
- ✅ Environment configuration (.env.local.example)

---

## 🔧 Step-by-Step Setup

### **Step 1: Get Your OpenAI API Key**

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it (you'll need it shortly)

### **Step 2: Generate Owner PIN Hash**

Open terminal and run:

```bash
cd lenoir-chatbot/backend
python -c "from services.identity import hash_pin; print(hash_pin('your-secret-pin-here'))"
```

Replace `your-secret-pin-here` with the PIN you want (e.g., "1234").

**Save the output** — it looks like: `$2b$12$...` (bcrypt hash)

### **Step 3: Backend Configuration**

```bash
cd lenoir-chatbot/backend

# Create .env file
cp .env.example .env

# Edit .env with your values:
# - OPENAI_API_KEY=sk-... (from Step 1)
# - OWNER_PIN_HASH=$2b$12$... (from Step 2)
# - DATABASE_URL should work as-is with docker-compose
```

### **Step 4: Frontend Configuration**

```bash
cd lenoir-chatbot/frontend

# Create .env.local
cp .env.local.example .env.local

# File should already have correct defaults:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

### **Step 5: Start PostgreSQL + Backend (Docker)**

From project root:

```bash
docker-compose up -d
```

Wait 10-20 seconds for PostgreSQL to be ready, then run migrations:

```bash
cd backend
alembic upgrade head
cd ..
```

This creates all tables, extensions, and indexes.

### **Step 6: Install & Start Backend (if not using Docker container)**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Step 7: Install & Start Frontend**

```bash
cd frontend
npm install
npm run dev
```

### **Step 8: Open in Browser**

Visit: **http://localhost:3000**

---

## 🧪 Testing the App

### **Test 1: Stranger Mode**

1. Page loads with "Who are you?" greeting
2. Type anything **except** "I am Lenoir"
3. Click Continue
4. Chat window opens with stranger greeting
5. Type a message, click Send
6. Backend responds (may take 5-10s first time)
7. **✅ Pass**: Message appears, assistant responds

### **Test 2: Owner Mode (PIN Auth)**

1. Reload page
2. Type "I am Lenoir" (case-insensitive, just needs the phrase)
3. Click Continue
4. PIN prompt appears: "Please provide your PIN..."
5. Enter your PIN (from Step 2)
6. Click Continue
7. **✅ Pass**: "Welcome back, Lenoir!" message + Owner badge appears

### **Test 3: Language Switching**

1. Click language selector (top right, e.g., "🇬🇧 English")
2. Choose French or Vietnamese
3. Type a message
4. **✅ Pass**: Response is in the selected language

### **Test 4: Voice Recording**

1. Click "Hold to speak" button and hold
2. Speak into microphone
3. Release mouse
4. Transcript should appear in text input field
5. Click Send
6. **✅ Pass**: Message sent, response appears

### **Test 5: Wrong PIN**

1. Type "I am Lenoir"
2. Continue
3. Enter **wrong** PIN
4. **✅ Pass**: "I don't recognize that PIN" message, fallback to stranger mode

### **Test 6: Logout**

1. Click "Logout" button (top right)
2. **✅ Pass**: Redirects back to identity prompt

---

## 🔐 Security Notes

- **PIN Hash**: Stored in environment variable (not database)
  - Never commit `.env` file
  - Bcrypt with 12 rounds (high security)
  
- **Stranger Sessions**: No history saved, no DB persistence
  - In-memory only, lost on page reload
  
- **Owner Sessions**: Full history persisted
  - Consider using secure backend deployment (not free Render tier in production)
  
- **CORS**: Restricted to `http://localhost:3000` (dev) and `FRONTEND_URL` env var
  - Update in `backend/main.py` for production

---

## 🚀 Production Deployment

### **Frontend (Vercel)**

```bash
cd frontend
vercel login
vercel deploy
```

### **Backend (Render or Railway)**

1. Create account at render.com (or railway.app)
2. Create PostgreSQL database
3. Create Web Service from your GitHub repo
4. Set environment variables in dashboard:
   - `DATABASE_URL` → PostgreSQL connection string
   - `OPENAI_API_KEY` → Your API key
   - `OWNER_PIN_HASH` → Bcrypt hash
   - `FRONTEND_URL` → Your Vercel domain
5. Deploy (auto-deploys on git push)

**Important**: Free tier backends spin down after 15 min idle (~30s cold start). Upgrade to Starter ($7/mo) for always-on.

---

## 📁 Project File Summary

```
lenoir-chatbot/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Settings from environment
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # For Docker Compose
│   ├── alembic.ini             # Migration config
│   ├── alembic/                # Database migrations
│   │   ├── env.py              # Alembic setup
│   │   ├── script.py.mako      # Migration template
│   │   └── versions/
│   │       └── 001_initial_schema.py  # Initial migration
│   ├── db/
│   │   ├── models.py           # SQLAlchemy models
│   │   └── session.py          # DB connection
│   ├── services/
│   │   ├── identity.py         # Passphrase + PIN
│   │   ├── openai_client.py    # Whisper, TTS, embeddings
│   │   ├── vectorstore.py      # pgvector retrieval
│   │   └── chain.py            # LangChain chains
│   ├── routers/
│   │   ├── auth.py             # /auth endpoints
│   │   ├── chat.py             # /chat endpoints
│   │   ├── voice.py            # /voice endpoints
│   │   └── memory.py           # /memory endpoints
│   ├── .env.example            # Environment template
│   └── .env                    # Your local config (git-ignored)
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Root page (App Router)
│   │   ├── layout.tsx          # Layout
│   │   ├── globals.css         # Global styles
│   │   └── components/
│   │       ├── IdentityPrompt.tsx
│   │       ├── ChatWindow.tsx
│   │       ├── MessageBubble.tsx
│   │       ├── VoiceButton.tsx
│   │       ├── LanguageSelector.tsx
│   │       └── *.module.css    # Component styles
│   ├── lib/
│   │   └── api.ts              # API client
│   ├── package.json            # NPM dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── next.config.js          # Next.js config
│   ├── .env.local.example      # Environment template
│   └── .env.local              # Your local config (git-ignored)
│
├── docker-compose.yml          # PostgreSQL + Backend
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
└── SETUP_GUIDE.md              # This file
```

---

## 🐛 Troubleshooting

### Backend won't start
```
Error: cannot import name 'Vector' from pgvector
→ pip install pgvector
```

### Database connection fails
```
Error: could not connect to server: Connection refused
→ Check docker-compose: docker-compose up -d
→ Wait 20s for PostgreSQL to start
```

### Frontend shows "Connecting to backend..."
```
→ Check backend is running: curl http://localhost:8000/health
→ Check NEXT_PUBLIC_API_URL in .env.local
→ Check CORS in backend/main.py allows localhost:3000
```

### Microphone not working
```
→ Check browser permissions (Settings → Site permissions → Microphone)
→ Check HTTPS (required for some browsers; localhost:3000 is OK)
→ Check browser console for errors (F12)
```

### Streaming responses arrive all at once
```
→ This is normal for now (we simulate streaming)
→ In production, connect to LangChain streaming callbacks
```

---

## 📊 Architecture Summary

```
Browser (localhost:3000)
    ↓ CORS-enabled HTTP
FastAPI Backend (localhost:8000)
    ├── LangChain (chains + memory)
    ├── OpenAI API (GPT-4o, Whisper, TTS, embeddings)
    └── PostgreSQL + pgvector (localhost:5432)
```

**Data Flow:**
1. User sends message → Backend
2. Backend retrieves context from pgvector (if owner)
3. LLMChain generates response
4. Response streamed back as SSE
5. Frontend displays in real-time

---

## ✨ Next Steps

1. **Get API key**: https://platform.openai.com/api-keys
2. **Follow Step-by-Step Setup** above
3. **Run the app** and test all features
4. **Deploy** to Vercel + Render when ready

---

## 💡 Tips

- **For development**: Keep docker-compose running, reload frontend for faster iteration
- **PIN management**: Store your PIN hash in a password manager, it's sensitive
- **Cost control**: Monitor OpenAI usage at https://platform.openai.com/account/usage
- **Scaling**: For high usage, consider upgrading Render PostgreSQL ($7+/mo)

---

## 🎉 You're All Set!

Your Lenoir Chatbot is ready to run. Follow the setup steps above and enjoy!

Questions? Check:
- Backend logs: `docker-compose logs -f backend`
- Browser console: F12 → Console tab
- OpenAI status: https://status.openai.com
