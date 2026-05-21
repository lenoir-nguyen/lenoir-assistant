# Architecture & Tech Stack

## Project Overview

**Lenoir Assistant** is a multilingual AI-powered assistant with persistent memory, voice capabilities, and intelligent conversation modes. It's built with Next.js (frontend), FastAPI (backend), OpenAI's GPT-4o, and PostgreSQL (v4+).

## Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Backend Server | FastAPI | 0.104.1 | Async HTTP API framework |
| Backend Runtime | Uvicorn | 0.24.0 | ASGI application server |
| LLM Integration | OpenAI SDK | 1.3.5 | GPT-4o API client |
| LLM Orchestration | LangChain | 0.1.17 | Conversation chains & memory (v4+) |
| Configuration | Pydantic | 2.4.2 | Settings management & validation |
| Authentication | bcrypt | 4.1.2 | PIN hashing (v3) |
| Cache Layer | Redis | 5.0.0 | Session token storage (v3) |
| Database (v4+) | PostgreSQL | Latest | Persistent conversation storage |
| ORM (v4+) | SQLAlchemy | 2.0.28 | Async database operations |
| Migrations (v4+) | Alembic | 1.13.1 | Database schema versioning |
| Vector DB (v5+) | pgvector | 0.2.4 | Semantic search for RAG |
| Frontend Framework | Next.js | 14.0.0 | Full-stack React app |
| UI Library | React | 18.2.0 | Component framework |
| Frontend Language | TypeScript | Latest | Type-safe JavaScript |
| Python Version | Python | 3.11+ | Backend runtime |
| Node Runtime | Node.js | 18+ | Frontend runtime |

## Project Structure

```
lenoir-assistant/
├── frontend/                          # Next.js 14 SPA
│   ├── app/
│   │   ├── page.tsx                  # Root page (renders ChatWindow)
│   │   ├── layout.tsx                # Root layout (metadata, fonts)
│   │   ├── globals.css               # Global styles (reset, base)
│   │   └── components/
│   │       ├── AuthScreen.tsx        # Login screen (v3, guest/owner modes)
│   │       ├── ChatWindow.tsx        # Main chat UI (state, history)
│   │       ├── MessageBubble.tsx     # Message display component (v2 TTS)
│   │       ├── LanguageSelector.tsx  # Language picker (en/fr/vi)
│   │       └── VoiceButton.tsx       # Microphone button (v2)
│   ├── lib/
│   │   └── api.ts                    # API client (sendMessage, login, transcribe, speak)
│   ├── package.json                  # Dependencies, scripts
│   ├── tsconfig.json                 # TypeScript config
│   ├── next.config.js                # Next.js config
│   ├── .env.local.example            # Env template (committed)
│   └── .gitignore
│
├── backend/                           # FastAPI REST API
│   ├── main.py                       # App entry, CORS, health check
│   ├── config.py                     # Settings class (Pydantic)
│   ├── routers/
│   │   ├── auth.py                   # POST /auth/login, /auth/logout (v3)
│   │   ├── chat.py                   # POST /chat/message (v4: LangChain + DB)
│   │   └── voice.py                  # POST /voice/transcribe, /voice/speak (v2)
│   ├── db/
│   │   ├── models.py                 # SQLAlchemy ORM models (v4+)
│   │   ├── session.py                # Async database connection (v4+)
│   │   └── utils.py                  # Database helper functions (v4+)
│   ├── services/
│   │   ├── identity.py               # Passphrase & PIN verification (v3)
│   │   ├── openai_client.py          # OpenAI API wrappers (transcribe, speak, embed)
│   │   ├── chain.py                  # LangChain chain builders (v4+)
│   │   └── vectorstore.py            # RAG/pgvector operations (v5+)
│   ├── tests/
│   │   ├── test_auth.py              # Authentication tests (v3)
│   │   ├── test_chat.py              # Chat endpoint tests
│   │   ├── test_voice.py             # Voice endpoint tests (v2)
│   │   └── test_*.py                 # Other test modules
│   ├── alembic/                      # Database migrations (v4+)
│   │   ├── env.py                    # Alembic configuration
│   │   ├── script.py.mako            # Migration template
│   │   └── versions/
│   │       └── 001_initial_schema.py # Initial schema migration
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Env template (committed)
│   └── .gitignore
│
├── docs/                             # Documentation
│   ├── VERSIONS.md                   # Release notes & roadmap
│   ├── SETUP_GUIDE.md                # Local setup & deployment
│   ├── ARCHITECTURE.md               # This file (tech stack & design)
│   ├── IMPLEMENTATION_SUMMARY.md     # Code walkthrough & testing
│   ├── PROMPT.md                     # Original project requirements
│   └── (skills/ and rules/ in root)
│
├── skills/                           # Reusable patterns & best practices
│   ├── multilingual-chat/SKILL.md
│   ├── fastapi-openai-integration/SKILL.md
│   ├── nextjs-chat-ui/SKILL.md
│   ├── langchain-database-patterns/SKILL.md
│   └── environment-secrets-management/SKILL.md
│
├── rules/                            # Coding standards & conventions
│   ├── python/
│   │   ├── fastapi.md
│   │   ├── testing.md
│   │   └── security.md
│   ├── typescript/
│   │   ├── nextjs.md
│   │   └── testing.md
│   └── common/
│       ├── multilingual.md
│       └── error-handling.md
│
├── CLAUDE.md                         # AI assistant guidance
├── README.md                         # Project overview
├── .claude/
│   └── settings.json                 # Claude Code project settings
├── .gitignore
└── .git                              # Git repository
```

## Features by Version

### v1.0.0 — Basic Chat SPA
- Real-time message exchange with GPT-4o
- Multilingual support (English, French, Vietnamese)
- Clean chat UI with timestamps
- Client-side message history (lost on refresh)

### v2.0.0 — Voice Features
- Voice input: Whisper STT
- Voice output: TTS speaker button
- Language-aware transcription & synthesis
- Graceful degradation if audio fails

### v3.0.0 — Authentication
- Owner login: Passphrase + PIN
- Redis bearer token authentication (24h TTL)
- Owner vs Guest modes with different system prompts
- Mode badge in UI

### v4.0.0 — LangChain & Database (In Progress)
- PostgreSQL persistent conversation storage
- LangChain ConversationChain orchestration
- Stateful backend (fetches history from DB)
- Owner: 10-message memory, persisted
- Guest: 5-message memory, in-memory only
- Session ID persistence in frontend

### v5.0.0 — RAG System (Planned)
- pgvector embeddings for semantic search
- Personal facts knowledge base
- Context-aware response augmentation
- Retrieval-augmented generation

## Architecture Diagrams

### Chat Flow (v3)
```
Frontend (sessionStorage: auth_token)
    ↓
POST /chat/message { message, language, history }
    ↓
Backend:
  1. Check auth (Redis: auth:{token})
  2. Select system prompt (owner or guest)
  3. Call OpenAI GPT-4o
  4. Return response
    ↓
Frontend (setMessages)
    ↓
Display in ChatWindow
```

### Chat Flow (v4+)
```
Frontend (sessionStorage: session_id, auth_token)
    ↓
POST /chat/message { message, session_id, language }
    ↓
Backend:
  1. Check auth (Redis: auth:{token})
  2. Get/create session (PostgreSQL)
  3. Fetch recent messages (DB query)
  4. Build LangChain chain
  5. Load memory with messages
  6. Call chain.apredict() → OpenAI
  7. Store response (DB insert)
  8. Return response + session_id
    ↓
Frontend (sessionStorage.setItem('session_id'))
    ↓
Display in ChatWindow
```

## API Endpoints

### Authentication (v3)
- `POST /auth/login` — Owner login (passphrase + PIN)
- `POST /auth/logout` — Invalidate token

### Chat
- `POST /chat/message` — Send message, get response (supports v3 auth header)

### Voice (v2)
- `POST /voice/transcribe` — Speech-to-text (Whisper)
- `POST /voice/speak` — Text-to-speech (TTS)

### Health
- `GET /health` — API status (includes Redis, database in v4+)

## Security

### Implemented
- ✅ API key not exposed to frontend
- ✅ CORS restricted to configured URL
- ✅ HTTPS in production
- ✅ Bearer token authentication (v3)
- ✅ PIN hashing with bcrypt (v3)
- ✅ Session isolation (Redis TTL, v3)

### To Be Added
- ⚠️ Rate limiting
- ⚠️ Input validation hardening
- ⚠️ Database encryption at rest (v4+)
- ⚠️ Audit logging

## Deployment

### Railway (Backend)
- Auto-deploys from GitHub on push to main
- Runs FastAPI in Docker container
- Database: PostgreSQL (v4+)
- Cache: Redis
- Environment variables via Railway dashboard

### Vercel (Frontend)
- Auto-deploys from GitHub on push to main
- Builds Next.js static/hybrid app
- CDN distribution
- Environment variables via Vercel dashboard

## Performance

| Metric | v3 | v4+ |
|--------|-----|-----|
| Chat latency | 0.5-3s | 0.5-3s (+ 10-50ms DB query) |
| Session creation | N/A | ~10ms |
| Memory fetch | N/A | ~20ms (last 10 messages) |
| Frontend bundle | ~200KB | ~200KB |
| Initial page load | 1-2s | 1-2s |

## Known Limitations

| Limitation | Fix Version |
|-----------|-------------|
| History lost on page reload | v4 (PostgreSQL) |
| No voice I/O | v2 (Whisper + TTS) |
| No authentication | v3 (Bearer tokens) |
| No cross-session memory | v4 (DB persistence) |
| No personalization | v5 (RAG system) |
