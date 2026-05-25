# Lenoir Assistant

A multilingual AI-powered assistant built with Next.js, FastAPI, and OpenAI's GPT-4o. Supports English, French, and Vietnamese with persistent memory, voice capabilities, and owner/guest modes.

**Live Demo:** [https://lenoir-chatbot.vercel.app](https://lenoir-chatbot.vercel.app)

**Production URLs:**
- **Frontend:** https://lenoir-chatbot.vercel.app
- **Backend API:** https://lenoir-chatbot-production.up.railway.app
- **GitHub:** https://github.com/lenoir-nguyen/lenoir-assistant

## Quick Start

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- OpenAI API key

### Local Development

**Backend (FastAPI):**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
uvicorn main:app --reload
```

**Frontend (Next.js):**
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local and add NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Visit `http://localhost:3000` and start chatting.

## Documentation

Start here: **[CLAUDE.md](CLAUDE.md)** — AI assistant guidance and project overview

Then explore:
- **[VERSIONS.md](docs/VERSIONS.md)** — Release notes for each version
- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** — Detailed setup instructions
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Tech stack and system design
- **[IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** — Code details and testing
- **[PROMPT.md](docs/PROMPT.md)** — Original project requirements
- **[skills/](skills/)** — Reusable patterns and best practices

## Project Structure

```
lenoir-assistant/
├── frontend/          # Next.js 14 application
├── backend/           # FastAPI application
├── docs/              # Documentation (VERSIONS, SETUP, ARCHITECTURE, etc.)
├── skills/            # Reusable patterns & best practices
├── rules/             # Coding standards & conventions
├── CLAUDE.md          # AI assistant guidance
└── README.md          # This file
```

## Tech Stack

- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.11, Uvicorn
- **API:** OpenAI GPT-4o
- **Deployment:** Vercel (frontend), Railway (backend)

## Features (v4 — Latest)

**Core Chat:**
- ✅ Real-time chat with GPT-4o
- ✅ Multilingual support (English, French, Vietnamese)
- ✅ Language switching mid-conversation
- ✅ Responsive design

**Persistence & Memory (v4):**
- ✅ **Persistent conversations** — Chat history stored in PostgreSQL
- ✅ **Session-based memory** — Conversations persist across page refreshes
- ✅ **Redis caching** — Fast response times and session management
- ✅ **Owner authentication** — PIN-based login (SHA-256 hashing)
- ✅ **Guest mode** — No login required, ephemeral sessions

**Voice & Accessibility:**
- ✅ Voice input — Record and transcribe with OpenAI Whisper
- ✅ Text-to-speech — Hear responses with natural audio
- ✅ Microphone recording — WebM format support

**Multi-User:**
- ✅ Owner mode — Full features with persistent memory
- ✅ Guest mode — Limited features, no persistence
- ✅ Session isolation — Each user has separate conversation history

## License

MIT
