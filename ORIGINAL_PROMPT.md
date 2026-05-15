# Lenoir Chatbot - Original Requirements & Prompt

This document captures the original user requirements that generated this entire project. Use this prompt with Claude Code to regenerate the project from scratch.

---

## 📝 Original User Request

**User's Goal**: 
*"I want to build a single page application which will have my personal AI assistant. I want that chatbot to be able to chat or speak with me (English, French or Vietnamese). The chatbot will ask who is joining the conversation at the beginning, if it's me by saying 'I am Lenoir', it can pull all the history and whatever it knows about me. If it's some body else, the chatbot will act like it's chatting with a stranger. If it's me, I want to build a memory system/database so that it can pull up whatever we had discussed (both by chat/text and voice). I want the frontend to be build by a React framework (maybe Next.js). I want the backend is a python framework (Flask or FastAPI). I want to use RAG to extend the memory of the chatbot. I want to use LangChain as the orchestration for the application. Please ask me any questions to clarify anything unclear. Also please let me know the options we have to host frontend, backend, db."*

---

## 🎯 Clarification Questions & Answers

### Question 1: Which LLM provider?
**Answer**: OpenAI (GPT-4o)
- Rationale: Best reasoning-to-speed ratio, streaming support, multimodal capable

### Question 2: Which voice stack (STT + TTS)?
**Answer**: OpenAI Whisper (STT) + TTS API
- Rationale: Multilingual, accurate, no local models needed, single provider with LLM

### Question 3: What memory/knowledge should be stored?
**Answer**: 
- Structured personal facts (manual entry with category + content)
- Personal documents/notes (PDF/TXT uploads)
- Conversation history (auto-embedded for RAG)

### Question 4: Identity/Authentication method?
**Answer**: Passphrase + Secret PIN
- Passphrase: "I am Lenoir" (case-insensitive)
- PIN: Bcrypt hashing (12 rounds) for security

### Question 5: Vector database choice?
**Answer**: pgvector (PostgreSQL extension)
- Rationale: Co-located with relational data, no separate service needed

### Question 6: History/Message database?
**Answer**: PostgreSQL (15+)
- Rationale: Reliable, ACID guarantees, pgvector integration, proven at scale

### Question 7: Hosting targets for free tier?
**Answer**: Cloud — free tier (Vercel + Render/Railway)
- Frontend: Vercel
- Backend: Render.com or Railway.app
- Database: Managed PostgreSQL included

### Question 8: Backend framework (Flask or FastAPI)?
**Answer**: FastAPI (Recommended)
- Rationale: Native async, auto-OpenAPI docs, streaming SSE support, faster startup

### Question 9: LLM change request (Claude vs OpenAI)?
**Answer**: Kept OpenAI GPT-4o
- Reason: Already using OpenAI for STT (Whisper), TTS, embeddings
- Using Claude would require 2 separate API keys (inefficient for first project)
- Single API key approach is more practical

---

## ✨ Derived Requirements

From the above, the following technical requirements were derived:

### Frontend Requirements
- Single Page Application (SPA)
- React framework (Next.js 14 with App Router)
- TypeScript for type safety
- Components:
  - Identity prompt (passphrase detection + PIN entry)
  - Chat window (message display, input, send)
  - Voice recording (hold-to-record button)
  - Language selector (en/fr/vi)
  - Message bubbles with timestamps
- Voice features:
  - Browser MediaRecorder for audio capture
  - Display transcript in input field
  - Auto-play TTS responses
- Multilingual UI (language selection per session)

### Backend Requirements
- Python web framework (FastAPI)
- Async/await support for non-blocking I/O
- Database ORM (SQLAlchemy 2.0+)
- Database migrations (Alembic)
- LangChain for orchestration
- OpenAI integrations (GPT-4o, Whisper, TTS, embeddings)
- Streaming SSE for real-time chat

### Database Requirements
- PostgreSQL 15
- Tables: sessions, messages, personal_facts, documents, document_chunks
- pgvector extension for semantic search
- Indexes on frequently queried columns

### Authentication Requirements
- Passphrase detection: "I am Lenoir" (case-insensitive)
- PIN verification: bcrypt hashing (12 rounds)
- Session tracking: owner vs. stranger distinction
- Stranger mode: no history persistence (privacy-by-design)

### RAG (Retrieval-Augmented Generation) Requirements
- Vector embeddings: OpenAI text-embedding-3-small (1536 dimensions)
- Storage: pgvector (Inverted File Flat index)
- Retrieval: Cosine distance similarity search (k=5 results)
- Sources: conversation history, personal facts, documents
- Context injection: Augment user prompt with retrieved facts before LLM

### Voice Requirements
- Speech-to-Text: OpenAI Whisper API with language hints
- Text-to-Speech: OpenAI TTS API (model: tts-1, voice: nova)
- Multilingual: STT/TTS support for en/fr/vi
- Streaming: SSE for real-time message delivery
- Audio format: WEBM (opus) for recording, MP3 for playback

### Deployment Requirements
- Frontend: Vercel (1-click from GitHub)
- Backend: Render.com or Railway.app
- Database: Managed PostgreSQL (included)
- Environment variables: API keys in .env (git-ignored)
- Docker: Docker Compose for local development

---

## 🏗️ Architecture Decisions

### 1. Conversation Modes
- **Owner Mode**: Full history, RAG retrieval, personal memory, persistent storage
- **Stranger Mode**: Stateless, 5-message memory window, no RAG, no persistence

### 2. Chain Strategy
- **Owner Chain**: LangChain LLMChain + ConversationBufferWindowMemory (10 msgs) + RAG augmentation
- **Stranger Chain**: LangChain LLMChain + ConversationBufferWindowMemory (5 msgs, in-memory only)

### 3. Streaming Approach
- Server-Sent Events (SSE) over HTTP/1.1
- Token-by-token delivery for real-time feedback
- Simpler than WebSockets, universal browser support

### 4. Security Strategy
- PIN hash stored in environment variable (never in database)
- CORS restricted to frontend URL
- SQL injection prevention via SQLAlchemy ORM
- Bcrypt 12-round cost factor for GPU-resistant hashing

### 5. API Design
- RESTful endpoints with JSON request/response
- Streaming SSE for chat responses
- File upload for documents
- Dependency injection for database sessions

---

## 📋 Deliverables Checklist

- [x] Next.js frontend SPA with TypeScript
- [x] FastAPI backend with async/await
- [x] PostgreSQL database with pgvector extension
- [x] SQLAlchemy ORM with Alembic migrations
- [x] LangChain orchestration (owner + stranger chains)
- [x] OpenAI integrations (GPT-4o, Whisper, TTS, embeddings)
- [x] Identity & authentication (passphrase + PIN)
- [x] RAG system (vector search + context injection)
- [x] Voice features (STT + TTS)
- [x] Multilingual support (en/fr/vi)
- [x] Docker Compose for local dev
- [x] Complete documentation (README, SETUP_GUIDE, etc.)
- [x] Git repository with GitHub MCP integration

---

## 🎯 Regeneration Instructions

To regenerate this project from scratch using Claude Code:

1. **Share this file** with Claude Code as context
2. **Ask Claude Code** to build Lenoir Chatbot following the requirements above
3. **Provide clarification** on any technical choices
4. **Claude Code will**:
   - Create project scaffold
   - Build backend (FastAPI + LangChain)
   - Build frontend (Next.js + React)
   - Create database models & migrations
   - Integrate OpenAI services
   - Set up Docker Compose
   - Write comprehensive documentation

**Expected Result**: Identical to the current Lenoir Chatbot project with all features working end-to-end.

---

## 📝 Notes for Future Reference

- All code is fully commented with inline explanations
- Architecture is extensible: easy to swap LLM, add new languages, modify prompts
- Security-first design: no secrets in code or git
- Production-ready: can deploy to Vercel + Render immediately
- Well-documented: setup, deployment, troubleshooting guides included

