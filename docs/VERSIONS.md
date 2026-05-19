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

## v4.0.0 — LangChain & Database (Planned)

**Planned Features**:
- Passphrase: "I am Lenoir"
- PIN protection with bcrypt hashing
- Owner vs. Stranger conversation modes
- Session management

---

## v4.0.0 — LangChain & Database (Planned)

**Planned Features**:
- PostgreSQL integration via Railway
- Persistent conversation memory
- LangChain orchestration
- ConversationBufferWindowMemory (last 10 messages for owner, 5 for stranger)
- System prompts with personalization

---

## v5.0.0 — RAG System (Planned)

**Planned Features**:
- pgvector for semantic search
- OpenAI embeddings
- Personal facts knowledge base
- Context-aware responses
- Retrieval-augmented generation

---
