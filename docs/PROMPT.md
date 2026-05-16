# Original Prompt (Rephrased for Clarity)

## Executive Summary

Build a sophisticated multilingual AI chat application called "Lenoir Chatbot" that grows through 5 incremental versions. The application supports real-time conversations in English, French, and Vietnamese. It's designed as a personal AI assistant with graduated feature complexity: starting with simple chat (v1), adding voice (v2), authentication (v3), persistent memory with LangChain (v4), and RAG-based personalization (v5).

---

## Core Requirements

### 1. Conversation Modes

The application must support two distinct user modes:

**Stranger Mode**:
- Anonymous user with no identity verification
- Limited conversation history (last 5 messages only)
- No access to personal facts or owner history
- Generic, helpful assistant personality
- Memory cleared on page reload
- No persistent data stored

**Owner Mode** (future, v3+):
- Authenticated with passphrase + PIN
- Extended conversation history (last 10 messages)
- Access to personal facts and owner-specific context
- Warm, personalized assistant personality
- History persists across sessions (v4+)
- Full RAG capabilities (v5+)

### 2. Multilingual Support

The chatbot must respond fluidly in three languages:

**Supported Languages**:
- English (en)
- French (fr)
- Vietnamese (vi)

**Requirements**:
- Language selector in UI (visible dropdown or buttons)
- User selects language, all responses adapt immediately
- System prompt includes language instruction
- Responses in user's selected language, never code-mixed
- All UI text also translates (future enhancement)

### 3. OpenAI Integration

**LLM Model**: GPT-4o (selected for quality and multimodal support)

**API Integration**:
- Direct OpenAI API calls in v1 (no LangChain middleware yet)
- Temperature: 0.7 (balanced creativity and consistency)
- Streaming enabled for real-time token delivery (v2+)
- Error handling for rate limits and API failures
- No caching of responses (fresh context each time)

### 4. Architecture & Stack

**Backend**:
- FastAPI (async, modern, automatic OpenAPI docs)
- Python 3.11+ (latest stable)
- Stateless design (client sends full history each request)
- CORS restricted to frontend URL only
- Health check endpoint for monitoring

**Frontend**:
- Next.js 14 with App Router (latest, React 18)
- TypeScript for type safety
- Client-side message history in React state (v1-v3)
- Database persistence (v4+)
- Responsive design (mobile-first)

**Deployment**:
- Backend: Railway (simple, auto-deploys from GitHub)
- Frontend: Vercel (native Next.js support)
- Both auto-deploy on push to main branch
- Secrets managed in environment variables (not in git)

### 5. Conversation Memory Strategy

**v1-v3** (Stateless):
- Message history in React state
- Lost on page reload
- Client sends full history with each request
- No database interaction
- Good for learning, bad for production UX

**v4** (Database-backed):
- PostgreSQL on Railway
- ConversationBufferWindowMemory from LangChain
- Owner: last 10 messages persisted
- Stranger: 5 messages, not persisted
- Automatic message archival
- Query history by user_id (v5+)

**v5** (RAG + Embeddings):
- pgvector extension for semantic search
- OpenAI embeddings for all messages and facts
- Personal facts knowledge base (markdown or structured)
- Retrieval-augmented generation (RAG)
- Context injection: relevant facts + recent history
- Semantic search for personalization

### 6. Voice Features (v2+)

**Input** (Speech-to-Text):
- OpenAI Whisper API for transcription
- Fallback to text input
- Audio input button toggle
- Transcript displayed before sending

**Output** (Text-to-Speech):
- TTS API (ElevenLabs or OpenAI TTS)
- Stream audio playback
- Pause/resume controls
- Speaker selection (v3+)

**UI Integration**:
- Microphone button in input area
- Speaker button for audio toggle
- Real-time waveform visualization (optional)

### 7. Authentication & Security (v3+)

**Owner Authentication**:
- Passphrase: "I am Lenoir" (magic phrase to unlock owner mode)
- PIN protection: 4-6 digit numeric PIN
- bcrypt hashing for PIN storage (never plaintext)
- Hash stored in `OWNER_PIN_HASH` environment variable
- Session tokens (JWT in v4+) for stateful auth
- Automatic logout after 30 min inactivity (v4+)

**Security Measures**:
- HTTPS only (enforced by Vercel/Railway)
- CORS restricted to frontend URL
- Environment variables for all secrets
- No secrets in version control (enforce via pre-commit hooks)
- Rate limiting (v4+) to prevent abuse
- Input sanitization (v4+)

### 8. LangChain Integration (v4+)

**Why LangChain**:
- Unified interface for memory, prompts, chains, agents
- Built-in conversation memory managers
- Easy integration with vector databases (pgvector)
- Streaming support for real-time responses
- Tool use for future expansion (v5+)

**Key Components**:
- `ConversationBufferWindowMemory`: Manages rolling window of messages
- `ChatPromptTemplate`: Dynamic prompt construction with variables
- `LLMChain`: Orchestrates LLM invocation with memory
- `PGVector`: Semantic search over embeddings
- `OpenAIEmbeddings`: Generate embeddings for indexing

**Implementation Flow**:
1. User sends message
2. LangChain memory loads recent history
3. System constructs prompt with context
4. LLMChain calls GPT-4o with full context
5. Response streamed back to frontend
6. New message saved to memory automatically

### 9. RAG System (v5)

**Knowledge Base**:
- Personal facts about Lenoir (markdown format)
- Examples: "Lenoir loves hiking", "Lenoir is a software engineer"
- Embedded using OpenAI embeddings
- Stored in pgvector

**Retrieval Flow**:
1. User question arrives
2. Semantic search via pgvector: find top 3 relevant facts
3. Inject facts into system prompt as context
4. LLM generates personalized response
5. Higher relevance = more personalized

**Example**:
```
User: "What's your favorite activity?"
Retrieval: [Fact 1: "loves hiking", Fact 2: "enjoys coding"]
Prompt: "You are Lenoir's assistant. Knowledge: loves hiking, enjoys coding."
Response: "Lenoir loves hiking and coding. I enjoy talking about both!"
```

---

## Version Roadmap

### v1 (Current) - Basic Chat SPA
**Goal**: Minimal working chat with language selection

**Build**:
- FastAPI backend with `/chat/message` endpoint
- Next.js frontend with ChatWindow component
- GPT-4o via direct OpenAI SDK calls
- Language selector (en/fr/vi)
- Client-side message history (React state)
- Deployed to Vercel + Railway

**Test**: Local end-to-end, then production URLs

**Learning Focus**: FastAPI basics, Next.js App Router, TypeScript, API design

**Deploy**: YES (Vercel + Railway)

---

### v2 - Voice Features
**Goal**: Add voice input and output

**Build**:
- Whisper API for speech-to-text
- TTS API for text-to-speech
- Audio input button + microphone permission handling
- Audio playback with controls
- Real-time streaming responses

**Changes**:
- New components: `AudioInput.tsx`, `AudioPlayer.tsx`
- Backend: `/chat/stream` endpoint for streaming responses
- Frontend: WebSocket or Server-Sent Events (SSE) for streaming

**Test**: Microphone + speaker on local, then production

**Learning Focus**: Audio APIs, streaming protocols, WebSocket/SSE

**Deploy**: YES (maintains backward compatibility)

---

### v3 - Authentication & Owner Mode
**Goal**: Multi-mode support with identity verification

**Build**:
- Passphrase verification ("I am Lenoir")
- PIN prompt with bcrypt validation
- Session management with tokens
- Stranger vs. Owner conversation modes
- Memory window distinction (5 vs. 10 messages)

**Changes**:
- New components: `AuthModal.tsx`, `PINEntry.tsx`
- Backend: `/auth/verify-passphrase`, `/auth/verify-pin` endpoints
- Database: Session table with user_id, token, expiry
- Request middleware: Check authorization header

**Test**: Both auth flows (stranger, owner), session expiry

**Learning Focus**: Authentication, session management, security best practices

**Deploy**: YES

---

### v4 - LangChain & Persistent Memory
**Goal**: Database-backed conversation memory

**Build**:
- PostgreSQL connection (Railway)
- LangChain ConversationBufferWindowMemory
- Chat history table (user_id, messages, timestamps)
- Automatic message persistence
- Memory querying by conversation_id

**Changes**:
- New file: `backend/db/models.py` with SQLAlchemy ORM
- New service: `backend/services/memory.py` for memory operations
- Update chat router: use LangChain memory instead of client-side history
- Frontend: no longer sends full history (backend manages it)
- New endpoint: `/chat/history?limit=50` for loading past conversations

**Test**: Persistence across page reloads, memory window management

**Learning Focus**: SQL, ORM (SQLAlchemy), LangChain memory, data persistence

**Deploy**: YES (includes DB migrations)

---

### v5 - RAG & Semantic Search
**Goal**: Personalized responses via knowledge base

**Build**:
- pgvector extension for semantic search
- Personal facts knowledge base (markdown import)
- OpenAI embeddings generation
- Retrieval-augmented generation pipeline
- Fact search by similarity (semantic)

**Changes**:
- New table: `personal_facts` (content, embedding, owner_id)
- New service: `backend/services/rag.py` for fact retrieval
- Update chat service: inject retrieved facts into prompt
- Frontend: admin panel to manage personal facts (add, delete, search)
- New endpoint: `/facts/*` for CRUD operations

**Test**: Fact retrieval accuracy, RAG context injection, personalization quality

**Learning Focus**: Semantic search, embeddings, RAG patterns, vector databases

**Deploy**: YES (includes pgvector setup script)

---

## Technology Rationale

### Why FastAPI?
- Modern, async-first framework (unlike Flask)
- Automatic request validation via Pydantic
- Zero-boilerplate OpenAPI documentation
- Perfect for learning REST API design
- Production-ready (used at Netflix, Uber)

### Why Next.js 14?
- App Router: file-based routing is intuitive
- Built-in optimizations: image, font, code splitting
- Server Components: better mental model for data fetching (v4+)
- Deployment to Vercel is one-click
- React 18 hooks for modern state management

### Why PostgreSQL + pgvector?
- Relational model for conversations + facts
- pgvector extension: native semantic search (no separate vector DB)
- Railway managed PostgreSQL: no ops overhead
- SQL is a fundamental skill worth learning
- LangChain has first-class support

### Why OpenAI GPT-4o?
- Best quality for conversational AI
- Multimodal (text + vision in future)
- Streaming support for real-time UX
- Cost-effective for the quality
- Largest ecosystem of integrations

### Why LangChain (v4+)?
- Unifies memory, chains, tools, agents
- ConversationBufferWindowMemory: perfect for rolling history
- RAG abstractions: retriever → chain pipeline
- Streaming first-class citizen
- Ecosystem: Langfuse tracing, LangSmith debugging

---

## Deployment Strategy

### Development Environment
- Local: `localhost:8000` (backend) + `localhost:3000` (frontend)
- Environment: `.env` and `.env.local` files (git-ignored)
- Database: local PostgreSQL (v4+, optional)

### Production Environment
- **Backend**: Railway
  - Auto-deploy on push to main
  - Environment variables set in Railway dashboard
  - Scales horizontally (multiple dynos)
  - PostgreSQL managed by Railway (v4+)

- **Frontend**: Vercel
  - Auto-deploy on push to main
  - CDN distribution (global)
  - Automatic HTTPS
  - Environment variables set in Vercel dashboard

### Secret Management
- **Project-local secrets** (`.env`, `.env.local`): Git-ignored, safe
- **Examples** (`.env.example`, `.env.local.example`): Committed, no real values
- **GitHub PAT + other global secrets**: `~/.claude/settings.local.json` (outside repo, outside git)
- **Production secrets**: Railway + Vercel dashboards (UI-only, never in git)

---

## Testing & Validation

### v1 Validation Checklist
- [ ] Backend starts: `uvicorn main:app --reload` without errors
- [ ] Health endpoint works: `curl http://localhost:8000/health`
- [ ] Frontend builds: `npm run build` with no TypeScript errors
- [ ] Frontend dev server runs: `npm run dev` at localhost:3000
- [ ] Can send message and receive response
- [ ] Language switching works (response changes language)
- [ ] Timestamps displayed correctly
- [ ] Auto-scroll on new message
- [ ] Vercel deployment succeeds
- [ ] Railway deployment succeeds
- [ ] Live URLs accessible end-to-end

### Later Versions
- Voice: microphone + speaker tests (mobile + desktop)
- Auth: both stranger + owner flows, session expiry
- Memory: persistence across page reload, memory window enforcement
- RAG: fact retrieval accuracy, semantic similarity ranking

---

## Success Criteria

### Per Version
- Code compiles/type checks without errors
- All endpoints respond correctly (tested with curl + UI)
- No secrets in version control
- Documentation is complete and accurate
- Production deployment succeeds
- End-to-end flow works locally and in production

### Overall Project
- User learns LangChain/RAG fundamentals
- User learns Next.js App Router patterns
- Clean GitHub history (no confidential information)
- Well-documented for future enhancement
- Reusable skills captured for future projects

---

## Documentation Requirements

### Root README.md
- Project overview (1-2 sentences)
- Quick start (backend + frontend commands)
- Link to `/docs` files with brief descriptions
- Tech stack summary
- Roadmap (v1-v5)

### /docs Folder Structure
1. **VERSIONS.md**: Brief entry per version (date, features, status)
2. **SETUP_GUIDE.md**: Local setup + production deployment (detailed)
3. **PROJECT_DETAILS.md**: Tech stack, architecture, file structure, API reference
4. **IMPLEMENTATION_SUMMARY.md**: Code walkthrough, testing procedures, debugging
5. **PROMPT.md**: This document (original requirements for AI regeneration)
6. **REUSABLE_SKILLS.md**: Patterns, best practices, lessons learned

---

## Reusable Skills for Future Projects

1. **Documentation structure**: 6-file pattern for comprehensive project documentation
2. **Environment secrets**: 3-tier approach (project local, examples, global)
3. **Git workflow**: Pull before push, no force pushes to main, clean commit messages
4. **Incremental versioning**: Build → Test → Deploy, then add next feature
5. **Monorepo structure**: /frontend, /backend, /docs organization
6. **Stateless API design**: Client sends full context, server doesn't maintain session
7. **Type safety**: TypeScript + Pydantic across entire stack
8. **Auto-deployment**: GitHub → Vercel/Railway pipeline
9. **CORS best practices**: Restrict to known origins only
10. **Async Python**: FastAPI + async/await for better concurrency

---
