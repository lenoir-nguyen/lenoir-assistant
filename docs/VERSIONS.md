# Version History

## v1.0.0 — Basic Chat SPA (2026-05-15)

**Status**: ✅ Complete & Deployed

**Features**:
- Text-based chat interface with real-time messaging
- Language selection (English, French, Vietnamese)
- GPT-4o model integration via OpenAI API
- Client-side message history (persisted in React state only)
- Auto-scroll to latest message
- Typing indicators ("Thinking...") during responses
- Responsive UI with message timestamps

**Files Created**:
- Backend: `main.py`, `config.py`, `routers/chat.py`, `requirements.txt`
- Frontend: `ChatWindow.tsx`, `MessageBubble.tsx`, `LanguageSelector.tsx`, `api.ts`
- Docs: `VERSIONS.md`, `SETUP_GUIDE.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_SUMMARY.md`, `PROMPT.md`
- Config: `package.json`, `tsconfig.json`, `next.config.js`, `.env.local.example`, `.env.example`

**Tech Stack**:
- Backend: FastAPI, Python 3.11+, OpenAI SDK
- Frontend: Next.js 14, React 18, TypeScript
- Deployment: Vercel (frontend), Railway (backend)

**Testing**: ✅ Local end-to-end working

---

## v2.0.0 — Voice Features (2026-05-19)

**Status**: ✅ Complete & Deployed

**Features**:
- Voice input: Speech-to-text (Whisper STT) via microphone
- Voice output: Text-to-speech (TTS) with per-message speaker button
- Transcription inserts into input field (user can edit before sending)
- Audio playback via speaker icon on assistant messages
- Language-aware TTS (responds in selected language)
- Graceful fallback if audio APIs fail

**New Components**:
- `VoiceButton.tsx` — Microphone recording button with visual feedback
- `backend/routers/voice.py` — Two endpoints: `/voice/transcribe` and `/voice/speak`
- `backend/tests/test_voice.py` — Comprehensive voice endpoint tests (TDD)

**API Changes**:
- New endpoints: `POST /voice/transcribe` (audio → text) and `POST /voice/speak` (text → audio)
- New config: `OPENAI_TTS_VOICE` (default: "nova")
- Frontend API functions: `transcribeAudio()` and `speakText()`

**Tech Stack Additions**:
- MediaRecorder API (native browser, no packages needed)
- OpenAI Whisper model (`whisper-1`)
- OpenAI TTS model (`tts-1`)

**Testing**: 
- Backend unit tests: 4 test cases (transcribe success/missing/empty, speak success/empty/missing)
- Frontend: VoiceButton component with microphone permission handling
- E2E: Mic recording → transcription → input → chat → TTS playback

**Key Design Decisions**:
- TTS is optional (speaker button, not auto-play) — respects user preferences
- Transcription shows in input field — user can verify/edit before sending
- Separate endpoints (not combined) — follows DRY principle
- No session ID persistence in v2 — stays in v4 with database

---

## v3.0.0 — Authentication (2026-05-19)

**Status**: ✅ Complete & Deployed

**Features**:
- Owner login: Passphrase ("i am lenoir") + 4-digit PIN authentication
- Bearer token-based session management (Redis, 24h TTL)
- Owner vs Guest conversation modes with different system prompts
- Mode badge in UI ("🔐 Owner Mode" or "👤 Guest Mode")
- Session persistence across page refreshes (sessionStorage)
- No authentication required for guest access

**New Components**:
- `AuthScreen.tsx` — Two-panel login interface (guest button + owner form)
- `backend/routers/auth.py` — Two endpoints: `POST /auth/login` and `POST /auth/logout`
- `backend/tests/test_auth.py` — Comprehensive auth tests (TDD, 5 test cases)

**API Changes**:
- New endpoints: `POST /auth/login` (passphrase + PIN → token), `POST /auth/logout` (invalidate token)
- Updated `POST /chat/message` to read Authorization header and use owner/guest system prompts
- New config: `OWNER_PIN_HASH` (bcrypt hash, set in Railway), `AUTH_TOKEN_TTL` (24h default)
- Frontend API function: `login(passphrase, pin)` returns token

**Tech Stack Additions**:
- bcrypt (4.1.2) for PIN hashing
- Redis for token storage (already deployed in v1)
- Bearer token authentication (no JWT, simple and stateless)

**System Prompts**:
- Owner: "You are Lenoir's personal AI assistant. You know Lenoir personally..."
- Guest: "You are a friendly AI assistant on Lenoir's personal chatbot..."

**Testing**:
- Backend unit tests: 5 test cases (login success/wrong pin/wrong passphrase, logout success/invalid)
- Integration tests: owner chat flow, guest chat flow
- Frontend: AuthScreen with guest access and owner login forms
- E2E: Auth → Chat with mode badge visible

**Key Design Decisions**:
- Redis-only tokens (no PostgreSQL yet) — simplicity, faster deployment
- Passphrase visible in system prompt check, PIN hashed in bcrypt — balance of security
- No token for guests — absence of header = guest mode
- Session token persists in sessionStorage, not persistent storage (cleared on close or refresh)
- TDD: all auth tests written before router implementation

---

## v4.0.0 — Persistent Conversations & Database (2026-05-25)

**Status**: ✅ Complete & Live in Production

**Frontend URL**: https://lenoir-chatbot.vercel.app  
**Backend URL**: https://lenoir-chatbot-production.up.railway.app  
**GitHub**: https://github.com/lenoir-nguyen/lenoir-assistant

**Major Features**:
- **PostgreSQL Persistence** — Conversations stored in production database
- **Session Management** — Unique session IDs, message history retrieval
- **Chat History Restoration** — Messages persist across page refreshes
- **Redis Caching** — Fast session lookups and token management
- **SHA-256 Authentication** — PIN-based owner login (secure hashing)
- **Multi-User Support** — Owner vs Guest modes with different persistence
- **LangChain Integration** — GPT-4o with conversation context

**Database Schema**:
- `sessions` table: UUID primary key, is_owner flag, language, created_at timestamp
- `messages` table: UUID primary key, session_id (FK), role, content, timestamps, indexed
- Indexes on session_id and created_at for fast retrieval

**API Endpoints**:
- `POST /auth/login` — PIN authentication (passphrase + PIN → token)
- `POST /chat/message` — Send message, get response, return session_id
- `GET /chat/history/{session_id}` — Retrieve complete conversation history
- `POST /voice/transcribe` — Speech-to-text transcription
- `POST /voice/speak` — Text-to-speech audio generation

**Infrastructure**:
- **Database**: PostgreSQL on Railway (with pgvector for future RAG)
- **Cache**: Redis on Railway for session tokens
- **Frontend**: Vercel with Next.js 14 (auto-deploy from GitHub)
- **Backend**: Railway with FastAPI (auto-deploy from GitHub)
- **AI**: OpenAI GPT-4o, Whisper STT, TTS

**Authentication**:
- Owner PIN: 9999 → SHA-256 hash: `888df25ae35772424a560c7152a1de794440e0ea5cfee62828333a456a506e05`
- Token TTL: 24 hours (86400 seconds)
- Bearer token in Authorization header
- Guest mode: No auth required, ephemeral sessions

**Testing**:
- ✅ All features verified in production
- ✅ Chat persistence working (tested with Playwright)
- ✅ Login/logout working
- ✅ Guest mode working
- ✅ Health endpoint: `{"status":"ok","redis":"connected","database":"connected"}`

**Environment Variables**:
```
OPENAI_API_KEY=sk-proj-...
DEBUG=false
FRONTEND_URL=https://lenoir-chatbot.vercel.app
OWNER_API_KEY_HASH=888df25ae35772424a560c7152a1de794440e0ea5cfee62828333a456a506e05
AUTH_TOKEN_TTL=86400
DATABASE_URL=postgresql://...
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
REDIS_URL=redis://...
```

**Key Changes from v3**:
- Switched from bcrypt to SHA-256 for PIN hashing (simpler, faster)
- Added PostgreSQL for message persistence (instead of Redis-only)
- Session IDs now generated per conversation (not per session)
- Chat history automatically retrieved on page refresh
- Owner and Guest conversations stored separately

**Tech Stack**:
- FastAPI + async SQLAlchemy 2.0
- Next.js 14 + React 18 + TypeScript
- PostgreSQL + Redis + OpenAI GPT-4o
- Alembic for database migrations
- Playwright for automated testing

---

## v5.0.0 — RAG System (Planned)

**Planned Features**:
- pgvector for semantic search and embeddings
- OpenAI embeddings integration
- Personal facts knowledge base
- Document upload and ingestion
- Context-aware retrieval-augmented generation
- Advanced conversation tagging and search

---
