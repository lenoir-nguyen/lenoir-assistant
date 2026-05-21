# Lenoir Assistant — Claude Code Project Guidance

## Project Overview

**Lenoir Assistant** is a multilingual AI-powered assistant with persistent memory, voice capabilities, and intelligent conversation modes. It's built with Next.js (frontend), FastAPI (backend), OpenAI's GPT-4o, and PostgreSQL (v4+).

**Purpose**: Personal AI assistant with owner/guest modes, supporting English, French, and Vietnamese.

**Status**: v3 deployed (authentication + voice) | v4 in progress (database + LangChain)

---

## Quick Reference

### Key Directories
```
lenoir-assistant/
├── frontend/app/components/
│   ├── ChatWindow.tsx        ← Main chat UI (state, message handling)
│   ├── AuthScreen.tsx        ← Login/guest access (v3)
│   └── VoiceButton.tsx       ← Microphone recording (v2)
├── frontend/lib/
│   └── api.ts               ← API client (sendMessage, login, transcribe, speak)
│
├── backend/routers/
│   ├── chat.py              ← Chat endpoint (v4: LangChain + database)
│   ├── auth.py              ← Authentication (v3: bearer tokens)
│   └── voice.py             ← Voice endpoints (v2: Whisper + TTS)
├── backend/db/
│   ├── models.py            ← Database schema (Session, Message, etc.)
│   ├── session.py           ← SQLAlchemy setup (async in v4)
│   └── utils.py             ← Database helpers (new in v4)
├── backend/services/
│   ├── identity.py          ← Passphrase + PIN verification
│   ├── chain.py             ← LangChain builders (v4)
│   └── vectorstore.py       ← RAG functions (future)
└── backend/alembic/
    └── versions/001_*.py    ← Database migrations (v4)
```

### Critical Files by Task

**Adding a feature:**
- Frontend: `frontend/app/components/ChatWindow.tsx` (state, handlers)
- Backend: `backend/routers/chat.py` (endpoint logic)
- API: `frontend/lib/api.ts` (client function)
- Tests: `backend/tests/test_*.py` (TDD)

**Database work (v4+):**
- Schema: `backend/db/models.py`
- Queries: `backend/db/utils.py`
- Migrations: `backend/alembic/versions/`

**Authentication (v3+):**
- Login logic: `backend/routers/auth.py`
- Verification: `backend/services/identity.py`
- Frontend flow: `frontend/app/components/AuthScreen.tsx`

---

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add OPENAI_API_KEY, DATABASE_URL (v4), REDIS_URL, OWNER_PIN_HASH
python -m uvicorn main:app --reload
```

**Health check**: `curl http://localhost:8000/health`

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local: set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

**Visit**: http://localhost:3000

### Database (v4+)
```bash
cd backend
alembic upgrade head  # Run migrations
```

---

## Key Commands

```bash
# Backend tests
pytest backend/tests/

# Frontend dev
npm run dev

# Backend dev
python -m uvicorn backend.main:app --reload

# Database migration (v4+)
alembic upgrade head
alembic downgrade -1  # Rollback

# Git workflow
git checkout -b v4/feature-name
git add .
git commit -m "feat: description"
git push origin v4/feature-name
# Create PR on GitHub
```

---

## Architecture Notes

### v3 (Current)
- **Chat**: Stateless backend, client sends full history
- **Auth**: Redis bearer tokens (24h TTL)
- **History**: Client-side only (React state)
- **Models**: GPT-4o direct calls

### v4 (In Progress)
- **Chat**: Stateful backend, fetches history from database
- **Auth**: Same Redis tokens (unchanged)
- **History**: PostgreSQL persistent storage
- **Models**: LangChain ConversationChain + GPT-4o
- **Memory**: Owner (10 messages), Guest (5 messages, in-memory)

### v5 (Planned)
- **RAG**: pgvector embeddings + personal facts database
- **Retrieval**: Semantic search for context augmentation

---

## Conversation Flow (v4)

```
Frontend (sessionStorage: session_id, auth_token)
    ↓
POST /chat/message { message, session_id, language }
    ↓
Backend:
  1. Check auth (Redis token)
  2. Fetch/create session (PostgreSQL)
  3. Fetch recent messages from DB
  4. Build LangChain chain (owner or guest)
  5. Load memory with previous messages
  6. Call chain.apredict() → OpenAI
  7. Store response in database
  8. Return response + session_id
    ↓
Frontend (store session_id in sessionStorage)
    ↓
Display response in ChatWindow
```

---

## Documentation Structure

- **[VERSIONS.md](docs/VERSIONS.md)** — Release notes (v1.0.0, v2.0.0, etc.)
- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** — Local + production setup
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Tech stack & system design
- **[IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** — Code walkthroughs
- **[PROMPT.md](docs/PROMPT.md)** — Original requirements (AI-regeneratable)
- **[skills/](skills/)** — Reusable patterns (multilingual, FastAPI, NextJS, etc.)
- **[rules/](rules/)** — Coding conventions (Python, TypeScript)

---

## When Working in Claude Code

### Use Agent Tool For:
- Complex multi-step refactors
- Cross-file consistency checks
- Architecture questions

### Use Plan Mode For:
- New features (v4, v5)
- Major refactors
- Architecture decisions

### Important Patterns:
- ✅ TDD: Write tests first (tests/ folder)
- ✅ Environment vars: .env (git-ignored), .env.example (committed)
- ✅ Async-first: Backend uses async/await (v4+)
- ✅ Error handling: FastAPI HTTPException for API errors
- ✅ Type safety: TypeScript frontend, Pydantic backend

---

## Common Workflows

### Adding a Chat Feature
1. Define feature in VERSIONS.md → plan the version
2. Create PR from v{N}/feature-name branch
3. Update tests first (tests/test_*.py)
4. Implement backend endpoint (routers/chat.py)
5. Update frontend component (ChatWindow.tsx)
6. Update API client (lib/api.ts)
7. Test end-to-end locally
8. Merge to main → auto-deploy to Railway + Vercel

### Debugging v3 Auth Issues
- Check Redis: `redis-cli` → `KEYS auth:*`
- Check tokens: Look for `auth:TOKEN` keys in Redis
- Check frontend: `sessionStorage.getItem('auth_token')`

### Debugging v4 Database Issues
- Check migrations: `alembic current`
- Check schema: `SELECT * FROM sessions;` in PostgreSQL
- Check logs: `docker logs railway-postgresql` (on Railway)

---

## Helpful Reminders

- **Git branch naming**: `v{VERSION}/feature-name` (e.g., `v4/langchain-integration`)
- **Commit style**: Semantic (feat:, fix:, docs:, refactor:, test:)
- **Testing**: Always run `pytest backend/tests/` before pushing
- **Secrets**: Never commit .env files; use .env.example templates
- **Async**: v4+ requires async/await for database calls
- **Language support**: Always test with en, fr, vi language codes

---

## Links

- **GitHub**: https://github.com/lenoir-nguyen/lenoir-assistant
- **Frontend (Vercel)**: https://lenoir-assistant.vercel.app
- **Backend (Railway)**: https://lenoir-assistant-api.railway.app
- **OpenAI**: https://platform.openai.com/api-keys
