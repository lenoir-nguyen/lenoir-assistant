# Lenoir Chatbot Project Prompt

## What to Build

A **multilingual AI chat SPA** (Single Page Application) that grows through 5 versions. Supports conversations in English, French, Vietnamese via GPT-4o.

## Core Features by Version

| Version | Features | Status |
|---------|----------|--------|
| **v1** | Text chat, language selector, client-side history | ✅ Done |
| **v2** | Voice input (Whisper) + voice output (TTS) | ⏳ Planned |
| **v3** | Auth (passphrase "I am Lenoir" + PIN), owner/stranger modes | ⏳ Planned |
| **v4** | PostgreSQL persistence, LangChain memory management | ⏳ Planned |
| **v5** | RAG system (pgvector, embeddings, personal facts) | ⏳ Planned |

## Tech Stack

**Backend**: FastAPI (Python 3.11+), stateless design, direct OpenAI API calls (v1), LangChain (v4+)

**Frontend**: Next.js 14 (App Router), React 18, TypeScript, client-side state (v1-v3)

**Deployment**: Vercel (frontend) + Railway (backend), auto-deploy on push to main

**Database** (v4+): PostgreSQL + pgvector

## v1 Specification

### Backend
- Endpoint: `POST /chat/message`
- Request: `{ message: string, language: "en"|"fr"|"vi", history: Message[] }`
- Response: `{ content: string, language: string }`
- Model: GPT-4o, temperature 0.7, streaming enabled
- System prompt: Instructs responses in selected language
- Health check: `GET /health` → `{ status: "ok" }`

### Frontend
- Components: ChatWindow, MessageBubble, LanguageSelector
- State: messages[], input, language, loading
- Language buttons: en/fr/vi selector
- Auto-scroll to latest message
- Message history in React state (cleared on reload)

### API Contract
```json
Request:
{
  "message": "Hello",
  "language": "en",
  "history": [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"}
  ]
}

Response:
{
  "content": "How can I help you?",
  "language": "en"
}
```

## Future Versions (Brief Overview)

**v2**: Add Whisper STT (speech-to-text) + TTS voice output, streaming responses via WebSocket/SSE

**v3**: Passphrase auth ("I am Lenoir") + PIN verification (bcrypt), owner vs stranger modes, session tokens

**v4**: PostgreSQL + LangChain ConversationBufferWindowMemory, persistent chat history, message archive

**v5**: pgvector semantic search, OpenAI embeddings, personal facts knowledge base, RAG context injection

## User Modes (v3+)

**Stranger** (no auth): 5-msg history max, no personal context, memory cleared on reload

**Owner** (with passphrase + PIN): 10-msg history max, access to personal facts (v5), persistent sessions (v4)

## Deployment

**Local**: `.env` (backend) + `.env.local` (frontend), both git-ignored

**Vercel** (frontend): Auto-deploy on push, set `NEXT_PUBLIC_API_URL` env var

**Railway** (backend): Auto-deploy on push, set `OPENAI_API_KEY` env var

**Secrets**: Store in environment dashboards (never in git). GitHub PAT in global `~/.claude/settings.local.json`

## Testing (v1)

- [ ] Backend: `uvicorn main:app --reload` starts without error
- [ ] Health check: `curl http://localhost:8000/health` returns `{"status":"ok"}`
- [ ] Frontend: `npm run build` passes TypeScript, `npm run dev` runs
- [ ] Send message → receive response
- [ ] Language switching works (French/Vietnamese responses verified)
- [ ] Vercel + Railway deployments succeed
- [ ] Live URLs work end-to-end

## Why This Stack?

- **FastAPI**: Modern async framework, automatic validation (Pydantic), zero boilerplate
- **Next.js 14**: App Router, built-in optimizations, one-click Vercel deploy
- **PostgreSQL + pgvector**: Relational database + native semantic search (no separate vector DB)
- **GPT-4o**: Best quality, multimodal, streaming support
- **LangChain** (v4+): Memory management, RAG abstractions

## Success Criteria

✅ Code compiles without errors  
✅ No secrets in version control  
✅ All features working per version  
✅ Local + production testing passes  
✅ Clean GitHub history (no credentials)
