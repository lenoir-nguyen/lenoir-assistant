# Lenoir Chatbot

A personal AI assistant with memory and voice capabilities. Features real-time chat with OpenAI GPT-4o, voice interaction (speech-to-text + TTS), English/French/Vietnamese support, owner authentication, and RAG-based personal memory system.

**Status**: ✅ Complete and Production-Ready  
**Quick Links**:
- 📖 [Project Details](PROJECT_DETAILS.md) — Features, tech stack, configuration, schema
- 🚀 [Setup Guide](SETUP_GUIDE.md) — Step-by-step local setup & testing
- 📝 [Original Prompt](ORIGINAL_PROMPT.md) — Requirements document (for regeneration)
- 🏗️ [Reusable Patterns](REUSABLE_SKILLS.md) — Code patterns for other projects

## 🏗️ Project Structure

```
lenoir-chatbot/
├── backend/           # FastAPI Python backend
├── frontend/          # Next.js React frontend
├── docker-compose.yml # Local development environment
└── README.md          # This file
```

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (for local dev with PostgreSQL)
- OpenAI API key
- A PIN for owner authentication (generate hash below)

## 🚀 Quick Start

### 1. Clone & Setup

```bash
cd lenoir-chatbot
```

### 2. Backend Setup

```bash
cd backend

# Copy environment template
cp .env.example .env

# Edit .env with your OpenAI API key and other settings
# IMPORTANT: Generate a PIN hash:
python -c "from services.identity import hash_pin; print(hash_pin('your-secret-pin-here'))"
# Copy the hash output and paste it as OWNER_PIN_HASH in .env

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend

# Copy environment template
cp .env.local.example .env.local

# Install dependencies
npm install
```

### 4. Database Setup (using Docker Compose)

From project root:

```bash
docker-compose up -d
```

This starts:
- PostgreSQL 15 with pgvector extension on `localhost:5432`
- FastAPI backend on `localhost:8000`

**First time only:** Run migrations
```bash
cd backend
alembic upgrade head
cd ..
```

### 5. Run Development Servers

**Backend** (in `backend/` directory):
```bash
uvicorn main:app --reload
```

**Frontend** (in `frontend/` directory):
```bash
npm run dev
```

Visit `http://localhost:3000` in your browser.

## 🔐 Owner Authentication

To identify as the owner "Lenoir":

1. Type "I am Lenoir" in the identity prompt
2. Enter your PIN when asked
3. Unlock personal memory and RAG retrieval

Generate your PIN hash (one-time):
```bash
python -c "from services.identity import hash_pin; print(hash_pin('your-pin-here'))"
```

Paste the hash as `OWNER_PIN_HASH` in `backend/.env`.

## 🌍 Languages

Supported: English (en), French (fr), Vietnamese (vi)

Select language in chat UI. Whisper STT and OpenAI TTS both support all three languages natively.

## 🗣️ Voice Features

- **Speech-to-Text**: Hold microphone button to record (browser MediaRecorder → OpenAI Whisper)
- **Text-to-Speech**: Assistant responses auto-play as audio via OpenAI TTS

## 💾 Memory Features

Owner sessions (after PIN verification) unlock:

- **Conversation History**: All messages are persisted and embedded for RAG
- **Personal Facts**: Manually add structured knowledge (e.g., preferences, contacts)
- **Document Upload**: Upload PDFs/TXT for context retrieval

Access via the UI memory management section.

## 🛠️ API Documentation

Once backend is running, visit:
```
http://localhost:8000/docs
```

Endpoints:
- `POST /auth/identify` — Identity claim (passphrase detection)
- `POST /auth/verify-pin` — PIN verification
- `POST /chat/message` — Chat (streaming SSE)
- `POST /voice/transcribe` — Speech-to-text
- `POST /voice/speak` — Text-to-speech
- `POST /memory/facts` — Add personal fact
- `POST /memory/upload` — Upload document
- `GET /memory/facts` — List facts

## 📦 Environment Variables

### Backend (`.env`)

```ini
DATABASE_URL=postgresql://user:pass@localhost:5432/lenoir_chatbot
OPENAI_API_KEY=sk-...
OWNER_PIN_HASH=$2b$12$...  # bcrypt hash from above
DEBUG=false
FRONTEND_URL=http://localhost:3000
```

### Frontend (`.env.local`)

```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

## 🐳 Docker Compose

Start local environment:
```bash
docker-compose up -d
```

Services:
- `postgres` — PostgreSQL 15 + pgvector, port 5432
- `backend` — FastAPI, port 8000 (runs automatically)

Stop:
```bash
docker-compose down
```

## 📋 Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14 (React 18) + TypeScript |
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL 15 + pgvector |
| LLM | OpenAI GPT-4o |
| STT | OpenAI Whisper API |
| TTS | OpenAI TTS API |
| Embeddings | OpenAI text-embedding-3-small |
| RAG Orchestration | LangChain |
| Streaming | Server-Sent Events (SSE) |

## 🚢 Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel deploy
```

### Backend (Render/Railway)

1. Commit to GitHub
2. Connect repo to Render/Railway
3. Set environment variables in dashboard
4. Deploy (auto-deploys on push)

Free tier: backend spins down after 15 min inactivity (~30s cold start). Upgrade to Render Starter ($7/mo) for always-on.

## 📝 Notes

- Stranger sessions: no history saved, no RAG retrieval
- Owner sessions: all messages embedded and stored for context
- PIN hash stored as env var (never in database) for security
- Streaming responses: chat tokens stream as SSE for real-time feedback
- Language: selected per-session, passed to Whisper & LLM

## 🐛 Troubleshooting

**Backend connection error?**
- Ensure backend is running: `http://localhost:8000/health`
- Check `DATABASE_URL` is correct
- Verify `OPENAI_API_KEY` is set

**Voice not working?**
- Check browser microphone permissions
- Verify `OPENAI_API_KEY` is valid
- Check browser console for errors

**Database not found?**
- Run: `docker-compose up -d`
- Then run migrations: `alembic upgrade head`

## 📄 License

Personal project. Built with ❤️
