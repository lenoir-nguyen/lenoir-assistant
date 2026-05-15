# Lenoir Chatbot - Project Details

**Status**: ✅ Complete and Production-Ready  
**Repository**: https://github.com/lenoir-nguyen/lenoir-chatbot  
**Last Updated**: 2026-05-14

---

## 🎯 What is Lenoir Chatbot?

Lenoir Chatbot is a **personal AI assistant single-page application** with voice interaction, intelligent memory retrieval, and multilingual support.

### Core Capabilities

- **💬 AI Chat** — Real-time streaming conversations powered by OpenAI GPT-4o
- **🎤 Voice Interaction** — Speak to chat (Whisper STT) and listen to responses (OpenAI TTS)
- **🌍 Multilingual** — English, French, Vietnamese (automatic language detection)
- **🔐 Private Access** — "I am Lenoir" passphrase + PIN authentication for owners
- **🧠 Personal Memory** — RAG-powered retrieval of conversation history, facts, and documents
- **👥 Guest Mode** — Stateless conversations for visitors (no data storage, privacy-by-design)

---

## 🏗️ Technology Stack

| Component | Technology | Version | Why Chosen |
|-----------|-----------|---------|-----------|
| **Frontend Framework** | Next.js | 14 | App Router, SSR, full-stack React |
| **Frontend Language** | TypeScript + React | 18 | Type safety, component reusability |
| **Backend Framework** | FastAPI | 0.104+ | Async, auto-docs, streaming SSE |
| **Backend Language** | Python | 3.11+ | Rich ML ecosystem, LangChain native |
| **Database** | PostgreSQL | 15 | Reliable, ACID, pgvector extension |
| **Vector Store** | pgvector | Built-in | Co-located with relational data |
| **ORM** | SQLAlchemy | 2.0+ | Async, type hints, migrations |
| **Migrations** | Alembic | Latest | Version-controlled schema evolution |
| **LLM** | OpenAI GPT-4o | Latest | Best reasoning, streaming, multimodal |
| **Speech-to-Text** | OpenAI Whisper API | Latest | Multilingual, accurate, no local model |
| **Text-to-Speech** | OpenAI TTS API | tts-1, voice: nova | Fast, natural sounding |
| **Embeddings** | OpenAI text-embedding-3-small | Latest | Cost-effective (1536 dims) |
| **Orchestration** | LangChain | 0.1+ | Standard RAG orchestration, memory |
| **Streaming** | Server-Sent Events (SSE) | HTTP/1.1 | Universal browser support |
| **Authentication** | bcrypt | 12 rounds | GPU-resistant PIN hashing |
| **Containerization** | Docker Compose | Latest | Reproducible local environment |
| **API Client** | Axios | Latest | Promise-based, interceptors |

### Why These Choices?

- **Next.js**: Full-stack React with App Router, built-in optimization, 1-click Vercel deploy
- **FastAPI**: Native async, automatic OpenAPI docs, excellent SSE streaming support
- **PostgreSQL + pgvector**: Single database for relational + vector data (no separate service)
- **OpenAI**: Single API key for LLM + voice + embeddings (cost-effective, consolidated)
- **SSE**: Simpler than WebSockets, universal browser support, fire-and-forget streaming
- **Docker Compose**: Reproducible local development with one `docker-compose up -d` command

---

## 🎯 Key Features Explained

### Identity & Authentication

**Flow:**
1. User types message
2. System detects "I am Lenoir" (case-insensitive)
3. If detected → Prompt for PIN
4. Verify PIN via bcrypt (never plain-text comparison)
5. Create owner session (or fallback to stranger)

**Key Details:**
- PIN hash stored in environment variable (never in database)
- Bcrypt 12-round cost factor (GPU-resistant, ~100ms per hash)
- Stranger sessions create no permanent records
- Owner sessions enable RAG and data persistence

### Conversation Modes

**Owner Mode** (authenticated via passphrase + PIN):
- All messages persisted to database
- Full conversation history available for RAG
- Personal facts and documents searchable
- 10-message conversation buffer in LLM memory
- Warm, personalized assistant tone
- Automatic RAG context injection

**Stranger Mode** (guest/no authentication):
- No messages saved to database
- 5-message in-memory buffer only (lost on reload)
- No RAG retrieval (no personal context)
- No document or fact access
- Friendly but generic assistant tone
- Privacy guaranteed: all data cleared on page reload

### RAG (Retrieval-Augmented Generation) System

**How it works:**

1. **User sends message** → Backend receives chat request
2. **Vector search** → Query pgvector for top-5 similar chunks using cosine distance
3. **Context retrieval** → Fetch matched facts, documents, conversation history
4. **Prompt augmentation** → Prepend retrieved context to user message
5. **LLM generation** → GPT-4o sees augmented prompt, generates personalized response
6. **Vector storage** → Embed and store response for future retrieval

**Vector Store Details:**
- Embeddings: OpenAI text-embedding-3-small (1536 dimensions)
- Index: IVFFlat (Inverted File Flat) for fast cosine similarity
- Sources: Conversation messages, personal facts, documents
- Search metric: Cosine distance (0 = identical, 2 = opposite)
- Default k-value: 5 results per query

### Voice Features

**Speech-to-Text Flow:**
1. User holds "Speak" button to record
2. Browser MediaRecorder captures audio (WebM, opus codec)
3. Frontend sends audio blob to `/voice/transcribe` endpoint
4. Backend calls OpenAI Whisper API (with language hint)
5. Whisper returns text transcript
6. Frontend displays transcript in chat input field

**Text-to-Speech Flow:**
1. Backend generates assistant response (GPT-4o)
2. Frontend detects response text
3. Sends text to `/voice/speak` endpoint with language
4. Backend calls OpenAI TTS API (model: tts-1, voice: nova)
5. Returns MP3 audio stream
6. Frontend plays audio via HTML5 `<audio>` element

### Multilingual Support

- **Languages**: English (en), French (fr), Vietnamese (vi)
- **Per-session selection**: User selects language dropdown, persists in session
- **Language hints**: Passed to Whisper for accurate transcription
- **System prompts**: LLM instructed to respond in selected language
- **Automatic**: TTS voice adapts to language for natural pronunciation

---

## 🔑 Critical Configuration

### OpenAI API Key
- **Status**: Provided by user (ndnduc@gmail.com)
- **Storage**: `backend/.env` (git-ignored for security)
- **Usage**:
  - GPT-4o for chat responses
  - Whisper API for speech-to-text
  - TTS API for text-to-speech
  - text-embedding-3-small for vector embeddings
- **Cost**: Monitor at https://platform.openai.com/account/usage

### Owner PIN Hash
- **Purpose**: Secure owner authentication via bcrypt
- **Generation**: `python -c "from services.identity import hash_pin; print(hash_pin('your-pin-here'))"`
- **Storage**: `backend/.env` → `OWNER_PIN_HASH=$2b$12$...`
- **Security**: 12-round bcrypt (GPU-resistant)
- **Do NOT share**: PIN hash is sensitive material

### GitHub Integration
- **MCP Enabled**: ✅ Yes (for automated git commits/pushes)
- **GitHub Token**: Stored in `.claude/settings.json` (not git-tracked)
- **Repository**: https://github.com/lenoir-nguyen/lenoir-chatbot
- **User**: lenoir-nguyen
- **Email**: ndnduc@gmail.com

---

## 🗄️ Database Schema

### Tables

#### `sessions` (UUID primary key)
- `id` (UUID) — Unique session identifier
- `is_owner` (boolean) — Owner (True) vs. Stranger (False)
- `language` (varchar) — Selected language (en/fr/vi)
- `created_at` (timestamp) — Session creation time

#### `messages` (UUID primary key)
- `id` (UUID) — Unique message identifier
- `session_id` (FK → sessions) — Parent session
- `role` (varchar) — 'user' or 'assistant'
- `content` (text) — Message text
- `modality` (varchar) — 'text' or 'voice'
- `language` (varchar) — Message language (en/fr/vi)
- `created_at` (timestamp) — Message timestamp
- **Index**: session_id, created_at

#### `personal_facts` (UUID primary key)
- `id` (UUID) — Unique fact identifier
- `session_id` (FK → sessions) — Owner session
- `category` (varchar) — Fact category (e.g., "Preferences", "Contacts")
- `content` (text) — Fact content
- `created_at` (timestamp) — Creation time

#### `documents` (UUID primary key)
- `id` (UUID) — Unique document identifier
- `session_id` (FK → sessions) — Owner session
- `filename` (varchar) — Original filename
- `description` (text) — User-provided description
- `created_at` (timestamp) — Upload time

#### `document_chunks` (UUID primary key)
- `id` (UUID) — Unique chunk identifier
- `source_type` (varchar) — 'conversation', 'document', or 'fact'
- `source_id` (UUID) — ID of source (message, document, or fact)
- `content` (text) — Chunk text
- `embedding` (vector(1536)) — OpenAI embedding (pgvector)
- **Index**: source_type, source_id, embedding (ivfflat cosine)

---

## 📡 API Endpoints

### Authentication
- `POST /auth/identify` — Detect passphrase ("I am Lenoir")
  - Request: `{ "message": string }`
  - Response: `{ "contains_passphrase": boolean }`

- `POST /auth/verify-pin` — Verify PIN against bcrypt hash
  - Request: `{ "session_id": string, "pin": string }`
  - Response: `{ "is_valid": boolean, "is_owner": boolean }`

### Chat
- `POST /chat/message` — Stream chat responses (SSE)
  - Request: `{ "session_id": string, "message": string, "language": string }`
  - Response: Server-Sent Events stream with tokens

### Voice
- `POST /voice/transcribe` — Speech-to-text (Whisper)
  - Request: multipart/form-data with audio blob + session_id + language
  - Response: `{ "transcript": string, "language": string }`

- `POST /voice/speak` — Text-to-speech (OpenAI TTS)
  - Request: `{ "session_id": string, "text": string, "language": string }`
  - Response: MP3 audio stream

### Memory (Owner Only)
- `POST /memory/facts` — Add personal fact
  - Request: `{ "session_id": string, "category": string, "content": string }`
  - Response: `{ "id": string, "category": string, "content": string }`

- `POST /memory/upload` — Upload document (PDF/TXT)
  - Request: multipart/form-data with file + session_id + description
  - Response: `{ "id": string, "filename": string }`

- `GET /memory/facts` — List all facts
  - Request: Query param `session_id`
  - Response: `[{ "id": string, "category": string, "content": string }, ...]`

### Health
- `GET /health` — Backend health check
  - Response: `{ "status": "ok" }`

---

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Browser                            │
│  (Next.js SPA @ Vercel: https://frontend-url)              │
└────────────────────────┬────────────────────────────────────┘
                         │ CORS-enabled HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  (Render/Railway: https://api-url)                          │
│  ├─ LangChain chains (owner + stranger)                     │
│  ├─ OpenAI API calls (GPT-4o, Whisper, TTS)               │
│  └─ Database session management                            │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL queries
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL 15 + pgvector                        │
│  (Render PostgreSQL: postgresql://...)                      │
│  ├─ Relational tables (sessions, messages, facts)           │
│  └─ Vector tables (document_chunks with embeddings)         │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Targets
- **Frontend**: Vercel (1-click from GitHub)
- **Backend**: Render.com or Railway.app
- **Database**: Managed PostgreSQL (included in both services)
- **Cost**: ~$5-15/month total for always-on tiers

---

## 🔐 Security Best Practices

### API Keys & Secrets
- ✅ Never hardcode secrets in code
- ✅ Store in `.env` file (git-ignored)
- ✅ Use environment variable injection at deployment
- ✅ Rotate OpenAI API key if exposed
- ✅ Store PIN hash in env var, never in database

### Database
- ✅ Use SQLAlchemy ORM (prevents SQL injection)
- ✅ Enforce UNIQUE constraints on keys
- ✅ Set password-protected PostgreSQL
- ✅ Use VPC/private networks in production

### Authentication
- ✅ PIN verified via bcrypt (never plain-text comparison)
- ✅ Passphrase is lowercase, case-insensitive
- ✅ Session isolation: owner ≠ stranger data
- ✅ Bcrypt 12-round cost factor (GPU-resistant)

### Frontend
- ✅ All API calls via Axios with error handling
- ✅ No sensitive data in localStorage
- ✅ Stranger mode: data cleared on reload

### CORS
- ✅ Restricted to `FRONTEND_URL` environment variable
- ✅ Prevents cross-origin attacks
- ✅ Whitelist known frontend domains only

---

## 📊 Key Metrics & Specifications

| Metric | Value | Notes |
|--------|-------|-------|
| **Conversation Buffer** | Owner: 10 msgs, Stranger: 5 msgs | LangChain memory window |
| **RAG Retrieval** | k=5 results | Top-5 similar chunks per query |
| **Embedding Dimensions** | 1536 | OpenAI text-embedding-3-small |
| **Vector Distance Metric** | Cosine Distance | pgvector ivfflat index |
| **Bcrypt Cost Factor** | 12 rounds | ~100ms hash time, GPU-resistant |
| **TTS Model** | tts-1 | Fast, natural-sounding |
| **TTS Voice** | nova | Warm, friendly tone |
| **LLM Model** | gpt-4o | Latest, most capable |
| **LLM Temperature** | 0.7 | Balanced creativity (0.0-1.0 scale) |
| **Streaming Protocol** | SSE | Real-time token delivery |
| **Audio Format** | WEBM (opus) | Recording codec |
| **Audio Format** | MP3 | Playback format |

---

## 📂 File Organization

```
lenoir-chatbot/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings from environment
│   ├── requirements.txt            # Python dependencies
│   ├── db/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   └── session.py             # Database session factory
│   ├── services/
│   │   ├── identity.py            # Passphrase + PIN logic
│   │   ├── openai_client.py       # OpenAI API wrappers
│   │   ├── vectorstore.py         # pgvector operations
│   │   └── chain.py               # LangChain builders
│   ├── routers/
│   │   ├── auth.py                # /auth endpoints
│   │   ├── chat.py                # /chat streaming
│   │   ├── voice.py               # /voice STT + TTS
│   │   └── memory.py              # /memory facts + docs
│   └── alembic/                   # Database migrations
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Root page (SPA entry)
│   │   ├── layout.tsx             # Root layout
│   │   ├── globals.css            # Global styles
│   │   └── components/
│   │       ├── IdentityPrompt.tsx
│   │       ├── ChatWindow.tsx
│   │       ├── MessageBubble.tsx
│   │       ├── VoiceButton.tsx
│   │       └── LanguageSelector.tsx
│   ├── lib/
│   │   └── api.ts                 # Axios API client
│   ├── package.json               # NPM dependencies
│   └── tsconfig.json              # TypeScript config
│
├── docker-compose.yml             # Local dev (PostgreSQL + backend)
├── .gitignore                     # Ignore .env, node_modules, etc.
├── README.md                      # Quick start overview
├── SETUP_GUIDE.md                 # Step-by-step setup instructions
├── ORIGINAL_PROMPT.md             # Original requirements
├── PROJECT_DETAILS.md             # This file
├── REUSABLE_SKILLS.md             # Patterns for other projects
└── IMPLEMENTATION_SUMMARY.md      # File-by-file implementation
```

---

## 🐛 Common Issues & Troubleshooting

### Backend won't start
```
Error: cannot import name 'Vector' from pgvector
Solution: pip install pgvector
```

### Database connection fails
```
Error: could not connect to server: Connection refused
Solution: docker-compose up -d
          Wait 20s for PostgreSQL to start
          Verify DATABASE_URL in .env
```

### Frontend shows "Connecting to backend..."
```
Solution: Check backend is running: curl http://localhost:8000/health
          Check NEXT_PUBLIC_API_URL in .env.local
          Check CORS in backend/main.py allows localhost:3000
```

### Microphone not working
```
Solution: Check browser permissions (Settings → Microphone)
          Ensure HTTPS (localhost:3000 is OK)
          Check browser console for errors (F12)
```

### OpenAI API errors
```
Error: Invalid API key / Rate limit exceeded
Solution: Verify OPENAI_API_KEY in .env
          Check quota at https://platform.openai.com/account/usage
          Wait a few minutes if rate limited
```

---

## 📚 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **LangChain**: https://python.langchain.com
- **Next.js**: https://nextjs.org/docs
- **PostgreSQL**: https://www.postgresql.org/docs
- **OpenAI API**: https://platform.openai.com/docs
- **pgvector**: https://github.com/pgvector/pgvector

---

## 🎉 Summary

**Lenoir Chatbot** is a fully-featured personal AI assistant with:
- ✅ Real-time streaming chat (GPT-4o)
- ✅ Voice interaction (Whisper + TTS)
- ✅ Multilingual support (en/fr/vi)
- ✅ Personal memory (RAG system)
- ✅ Owner authentication (passphrase + PIN)
- ✅ Guest mode (privacy-by-design)
- ✅ Production-ready architecture
- ✅ Complete documentation
- ✅ Reusable design patterns

**Next**: Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) to run locally or deploy to production.

