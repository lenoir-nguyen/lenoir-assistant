# Project Details

## Overview

Lenoir Chatbot is a multilingual AI chat application built with a modern tech stack. It supports real-time conversations in English, French, and Vietnamese, powered by OpenAI's GPT-4o model. The project is designed to grow incrementally through 5 versions, adding features progressively.

## Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Backend Server | FastAPI | 0.104.1 | Async HTTP API framework |
| Backend Runtime | Uvicorn | 0.24.0 | ASGI application server |
| LLM Integration | OpenAI SDK | 1.3.5 | GPT-4o API client |
| Configuration | Pydantic | 2.4.2 | Settings management & validation |
| Frontend Framework | Next.js | 14.0.0 | Full-stack React app |
| UI Library | React | 18.2.0 | Component framework |
| Frontend Language | TypeScript | Latest | Type-safe JavaScript |
| Python Version | Python | 3.11+ | Backend runtime |
| Node Runtime | Node.js | 18+ | Frontend runtime |

## Project Structure

```
lenoir-chatbot/
├── frontend/                          # Next.js 14 SPA
│   ├── app/
│   │   ├── page.tsx                  # Root page (renders ChatWindow)
│   │   ├── layout.tsx                # Root layout (metadata, fonts)
│   │   ├── globals.css               # Global styles (reset, base)
│   │   └── components/
│   │       ├── ChatWindow.tsx        # Main chat UI (state, history)
│   │       ├── MessageBubble.tsx     # Message display component
│   │       └── LanguageSelector.tsx  # Language picker (en/fr/vi)
│   ├── lib/
│   │   └── api.ts                    # sendMessage() function
│   ├── package.json                  # Dependencies, scripts
│   ├── tsconfig.json                 # TypeScript config
│   ├── next.config.js                # Next.js config
│   ├── .env.local.example            # Env template (committed)
│   ├── .env.local                    # Actual env (git-ignored)
│   └── .gitignore
│
├── backend/                           # FastAPI REST API
│   ├── main.py                       # App entry, CORS, health check
│   ├── config.py                     # Settings class (Pydantic)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── chat.py                   # POST /chat/message endpoint
│   ├── requirements.txt              # Dependencies
│   ├── .env.example                  # Env template (committed)
│   ├── .env                          # Actual env (git-ignored)
│   └── .gitignore
│
├── docs/                             # Documentation
│   ├── VERSIONS.md                   # Version history & roadmap
│   ├── SETUP_GUIDE.md                # Setup & deployment
│   ├── PROJECT_DETAILS.md            # This file
│   ├── IMPLEMENTATION_SUMMARY.md     # Code walkthrough & testing
│   ├── PROMPT.md                     # Original requirements
│   └── REUSABLE_SKILLS.md            # Patterns for reuse
│
├── README.md                         # Project overview (root)
├── .gitignore                        # Git ignore rules
└── .git                              # Git repository

```

## Features (v1.0.0)

### Text Chat
- Real-time message exchange with OpenAI GPT-4o
- Streaming responses with token-by-token delivery
- Message history per session (client-side state)
- Typing indicators ("Thinking...") during generation

### Multilingual Support
- Language selector: English (🇬🇧), French (🇫🇷), Vietnamese (🇻🇳)
- System prompts adapted per language
- Responses automatically in selected language
- Language selection persistent during session

### User Interface
- Clean, minimal chat interface
- Message bubbles with timestamps
- Auto-scroll to latest message
- Disabled input during API response
- Responsive design for mobile/desktop

### Architecture
- Stateless backend (no session storage)
- Client-side message history in React state
- Client sends full history with each request
- CORS configured for frontend URL
- Health check endpoint for monitoring

## API Contract

### POST /chat/message

**Request**:
```json
{
  "message": "Hello, how are you?",
  "language": "en",
  "history": [
    {
      "role": "user",
      "content": "Hi there"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help?"
    }
  ]
}
```

**Response**:
```json
{
  "content": "I'm doing great! How can I assist you today?",
  "language": "en"
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid request (missing fields)
- `500`: Server error (API key issue, OpenAI error)

### POST /voice/transcribe (v2)

**Purpose**: Convert speech audio to text using OpenAI Whisper

**Request**:
- Content-Type: `multipart/form-data`
- Body: File upload with `audio` field (supported formats: webm, wav, mp4, flac)

**Response**:
```json
{
  "text": "Hello, how are you?"
}
```

**Status Codes**:
- `200`: Success
- `422`: Missing audio file or validation error
- `400`: Invalid audio format
- `500`: OpenAI API error

**Example (Frontend)**:
```typescript
const formData = new FormData()
formData.append('audio', audioBlob)
const response = await fetch('/voice/transcribe', {
  method: 'POST',
  body: formData
})
const { text } = await response.json()
```

### POST /voice/speak (v2)

**Purpose**: Convert text to speech using OpenAI TTS

**Request**:
```json
{
  "text": "Hello, how are you?",
  "language": "en"
}
```

**Response**:
- Content-Type: `audio/mpeg` (mp3 audio stream)
- Body: MP3 audio data that can be played directly

**Status Codes**:
- `200`: Success
- `422`: Missing or empty text field
- `500`: OpenAI API error

**Example (Frontend)**:
```typescript
const response = await fetch('/voice/speak', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Hello', language: 'en' })
})
const audioBlob = await response.blob()
const audio = new Audio(URL.createObjectURL(audioBlob))
audio.play()
```

### GET /health

**Response**:
```json
{
  "status": "ok",
  "redis": "connected"
}
```

**Status Codes**:
- `200`: Always succeeds (even if Redis is down)

## Configuration

### Backend Environment Variables

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | `sk-proj-...` | OpenAI API authentication |
| `DEBUG` | No | `false` | Enable debug logging |
| `FRONTEND_URL` | No | `http://localhost:3000` | CORS allowed origin |

### Frontend Environment Variables

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API URL (public, sent to browser) |
| `NEXT_PUBLIC_FRONTEND_URL` | No | `http://localhost:3000` | Frontend URL for self-reference |

## Security Considerations (v1)

### ✅ Secure in v1
- API key not exposed to frontend (only sent from backend)
- CORS restricted to configured frontend URL
- HTTPS in production (Vercel auto-enables)
- Session history cleared on page reload

### ⚠️ To Be Secured in Later Versions
- No authentication (added in v3 with PIN)
- No persistent history (added in v4 with database)
- No rate limiting (will add in future versions)
- No input validation beyond basic checks (will harden)

## Known Limitations

| Limitation | Version Addressed | Details |
|-----------|------------------|---------|
| Session history lost on reload | v4 | Database persistence will save history |
| No voice input/output | v2 | Whisper STT + TTS coming in v2 |
| No authentication | v3 | PIN + passphrase authentication in v3 |
| No memory across sessions | v4 | PostgreSQL + LangChain memory in v4 |
| No personalization | v5 | RAG system with personal facts in v5 |
| No real-time streaming UI | v2 | Voice features will include real-time UI |

## Data Flow

```
User Input (ChatWindow)
    ↓
sendMessage() API call
    ↓
Backend: POST /chat/message
    ↓
OpenAI API: GPT-4o completion
    ↓
Response: JSON with content + language
    ↓
setMessages() adds to React state
    ↓
MessageBubble components re-render
```

## Performance Characteristics

### Backend
- **Request latency**: ~0.5-3 seconds (depends on response length)
- **Concurrent requests**: Uvicorn handles ~100 concurrent connections
- **Memory usage**: ~200-300MB (Python runtime + FastAPI)
- **Startup time**: ~2-3 seconds

### Frontend
- **Bundle size**: ~200KB (Next.js + React + UI code, gzipped)
- **Initial page load**: ~1-2 seconds (localhost) / ~2-4 seconds (production)
- **Time to interactive**: ~1-2 seconds
- **Message send-to-display**: ~0.5-3 seconds (network + backend latency)

## Deployment Platforms

### Railway (Backend)
- Runs FastAPI server in Docker container
- Auto-deploys from GitHub on push to main
- Scales horizontally (multiple dyno types available)
- Environment variables set in Railway dashboard
- Public URL: `https://project-name-production.up.railway.app`

### Vercel (Frontend)
- Builds Next.js app, serves from CDN
- Auto-deploys from GitHub on push to main
- Includes serverless functions (API routes if needed)
- Environment variables set in Vercel dashboard
- Public URL: `https://project-name.vercel.app`

## Dependencies Explanation

### Backend

**fastapi** (0.104.1)
- Modern async web framework for building REST APIs
- Automatically generates OpenAPI documentation
- Type hints enable automatic request/response validation

**uvicorn** (0.24.0)
- ASGI server to run FastAPI
- Handles HTTP requests and WebSocket connections
- Includes auto-reload for development

**openai** (1.3.5)
- Official OpenAI SDK
- Simplifies GPT-4o API calls
- Handles authentication and error handling

**python-dotenv** (1.0.0)
- Loads environment variables from `.env` file
- Keeps secrets out of version control

**pydantic** (2.4.2)
- Data validation using Python type hints
- Automatic JSON serialization/deserialization
- Runtime type checking

**pydantic-settings** (2.0.3)
- Extension of Pydantic for managing settings
- Loads config from environment variables
- Type-safe configuration management

### Frontend

**next** (14.0.0)
- React framework with file-based routing
- Server-side rendering, static generation, incremental static regeneration
- Built-in optimization for images, fonts, code splitting
- App Router (new default) uses /app directory

**react** (18.2.0)
- JavaScript library for building user interfaces
- Component-based architecture
- State management with hooks (useState, useEffect, useRef)

**react-dom** (18.2.0)
- React library for rendering to the browser DOM
- Bundled with React as of v18

**typescript** (latest)
- Adds static type checking to JavaScript
- Catches errors at development time
- Improves IDE autocomplete and refactoring

---
