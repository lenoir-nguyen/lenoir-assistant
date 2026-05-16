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

## v2.0.0 — Voice Features (Planned)

**Planned Features**:
- Voice input (Whisper STT)
- Voice output (TTS API)
- Voice button toggle in UI
- Audio streaming

---

## v3.0.0 — Authentication (Planned)

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
