# Implementation Summary

## Backend Implementation

### Overview
The backend is a stateless FastAPI server that receives chat messages, sends them to OpenAI's GPT-4o model with language-aware system prompts, and returns responses. All conversation history is managed by the client.

### File: `main.py`

**Purpose**: Application entry point, CORS setup, health check

**Key Code Sections**:
- FastAPI app initialization with metadata
- CORSMiddleware configured to allow `localhost:3000` and `FRONTEND_URL` env variable
- GET `/health` endpoint returning `{"status": "ok"}`
- Router inclusion for chat routers

**CORS Security**: Restricts API calls to frontend URL only, preventing unauthorized cross-origin requests

### File: `config.py` (v4 with v4.1 Fact Caching)

**Purpose**: Centralized settings management using Pydantic

**Key Settings** (v4+):
- `OPENAI_API_KEY` (required) - OpenAI API key
- `DEBUG` (optional, default False) - verbose logging
- `FRONTEND_URL` (optional) - CORS configuration
- `DATABASE_URL` (v4) - PostgreSQL connection string
- `REDIS_URL` (v4) - Redis connection string
- `AUTH_TOKEN_TTL` (v4) - Token expiration (24h default)
- `OWNER_PIN_HASH` (v4) - Hashed owner PIN

**v4.1 Fact Caching Settings**:
```python
FACT_CACHE_TTL_OWNER: int = 86400  # 24 hours for owners
FACT_CACHE_TTL_GUEST: int = 3600   # 1 hour for guests
FACT_CACHE_MAX_ITEMS: int = 50     # Max facts per session
FACT_EXTRACTION_ENABLED: bool = True  # Can be disabled globally
```

**How it works**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"
    DATABASE_URL: str
    REDIS_URL: str
    FACT_CACHE_TTL_OWNER: int = 86400
    FACT_CACHE_TTL_GUEST: int = 3600
    FACT_EXTRACTION_ENABLED: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### File: `routers/voice.py` (v2)

**Purpose**: Voice transcription and synthesis endpoints using OpenAI APIs

**Data Models**:
```python
class TranscribeResponse(BaseModel):
    text: str

class SpeakRequest(BaseModel):
    text: str
    language: str
```

**POST /voice/transcribe Endpoint** (Speech-to-Text):
1. Receive audio file as multipart form data
2. Call `openai.audio.transcriptions.create(model="whisper-1", file=audio)`
3. Extract transcribed text
4. Return `TranscribeResponse` with text

**POST /voice/speak Endpoint** (Text-to-Speech):
1. Receive `SpeakRequest` with text and language
2. Call `openai.audio.speech.create(model="tts-1", voice=tts_voice, input=text)`
3. Stream MP3 audio response directly to client
4. Return `StreamingResponse` with audio/mpeg content type

**Key Design**:
- Transcription uses Whisper for accurate multi-language support
- TTS uses OpenAI voices (default: "nova")
- Audio streaming allows immediate playback without buffering full file
- No session storage — stateless like v1

### File: `routers/chat.py` (v4 with v4.1 Fact Caching)

**Purpose**: Chat message endpoint with OpenAI integration, database persistence, and fact caching

**Data Models** (v4+):
```python
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    message: str
    language: str  # "en", "fr", "vi"
    session_id: str | None = None  # v4: session UUID for persistence

class ChatResponse(BaseModel):
    content: str
    language: str
    session_id: str  # v4: return session for frontend persistence
```

**POST /chat/message Endpoint** (v4 Workflow):
1. Check if user is authenticated as owner (bearer token)
2. Get or create session in PostgreSQL (or use existing session_id)
3. Store user message in database
4. **[v4.1] Extract facts** from user message using pattern matching
5. **[v4.1] Cache facts** in Redis with role-based TTL (24h owner, 1h guest)
6. **[v4.1] Store owner facts** permanently in PostgreSQL
7. Fetch recent message history from database
8. **[v4.1] Retrieve cached facts** for inclusion in system prompt
9. Build LangChain conversation with context
10. Call `client.chat.completions.create()` with facts in system prompt
11. Store assistant response in database
12. Return `ChatResponse` with session_id for frontend

**System Prompt** (v4.1 with facts):
```
## Remembered Facts
**Personal Preference:**
- My birthday is May 15
- My favorite food is pizza

[rest of system prompt...]
```

**Error Handling** (v4+):
- Session management errors: 500 with details
- OpenAI API error: 500 with error details
- Database errors: gracefully logged, continues if non-critical
- Redis fact caching errors: non-critical (fact still cached), logged as warning

### File: `services/fact_extractor.py` (v4.1)

**Purpose**: Extract facts from user messages using pattern-based regex matching

**Data Model**:
```python
@dataclass
class Fact:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str  # "event", "personal_preference", "contact", "habit"
    content: str   # Extracted fact text
    raw_statement: str  # Original user text
    created_at: datetime = field(default_factory=datetime.utcnow)
```

**Pattern Examples**:
```python
# "My birthday is May 15" → category: "event", content: "My birthday is May 15"
# "I like pizza" → category: "personal_preference", content: "I like pizza"
# "I work at Acme Corp" → category: "contact", content: "I work at Acme Corp"
# "My phone is 555-1234" → category: "contact", content: "My phone is 555-1234"
```

**`extract_facts(user_message: str)` Function**:
1. Iterate through regex patterns (birthday, preferences, contact, work, hobbies, etc.)
2. Find all matches in user message
3. Categorize each match (event, personal_preference, contact, habit)
4. Create `Fact` objects with category, content, and raw statement
5. Return list of `Fact` objects
6. Gracefully ignore non-matching messages (no error if no facts found)

**Design Decision**: Uses regex patterns (no LLM call) for:
- Speed: ~10-50ms per message
- Cost: No additional API calls
- Reliability: Patterns are explicit, no hallucinations

### File: `services/fact_manager.py` (v4.1)

**Purpose**: Manage Redis caching and database persistence of facts

**Key Functions**:

`cache_fact(session_id: str, fact: Fact, ttl: int = 86400) -> bool`:
- Store fact in Redis with TTL (default 24h)
- Key pattern: `facts:{session_id}:{fact_id}`
- Maintain index: `facts:session:{session_id}` → set of fact IDs
- Try-except blocks wrap all Redis operations (non-critical if index fails)
- Returns True if cached, False if error

`get_cached_facts(session_id: str) -> list[Fact]`:
- Retrieve all cached facts for session
- Query index `facts:session:{session_id}` to get fact IDs
- Fetch each fact from `facts:{session_id}:{fact_id}`
- Deserialize back to `Fact` objects
- Returns list (empty if none found)

`clear_session_facts(session_id: str) -> bool`:
- Delete all facts for session (on logout or session clear)
- Delete individual facts and the index
- Try-except blocks prevent crashes if Redis unavailable
- Returns True if successful, False otherwise

`format_facts_for_context(facts: list[Fact]) -> str`:
- Format facts into markdown string for system prompt
- Group by category with headers
- Example output:
```
## Remembered Facts

**Contact:**
- I work at Acme Corp
- My phone is 555-1234

**Personal Preference:**
- I like pizza
- My favorite color is blue

Use these facts to provide personalized responses.
```

**Design Decisions**:
- Redis for fast short-term caching (1-5ms operations)
- Role-based TTL: Owners 24h (86400s), Guests 1h (3600s)
- Index tracking is non-critical (try-except prevents crashes)
- PostgreSQL only for owners (permanent storage via `store_personal_fact`)

---

## Frontend Implementation

### Overview
The frontend is a Next.js 14 SPA with React hooks for state management. It maintains message history in React state, handles language selection, and communicates with the backend API.

### File: `app/page.tsx`

**Purpose**: Root page (index)

**Key Code**:
```typescript
'use client'
import ChatWindow from './components/ChatWindow'

export default function Page() {
  return (
    <main style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <ChatWindow />
    </main>
  )
}
```

Note: `'use client'` makes this a Client Component, allowing React hooks

### File: `app/layout.tsx`

**Purpose**: Root layout applied to all pages

**Key Code**:
```typescript
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Lenoir Chatbot',
  description: 'A simple AI chat assistant',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

### File: `app/components/ChatWindow.tsx`

**Purpose**: Main chat interface and state management

**State Management**:
```typescript
const [messages, setMessages] = useState<Message[]>([
  { id: '0', role: 'assistant', content: 'Hello! How can I help you today?', timestamp: new Date() },
])
const [input, setInput] = useState('')
const [language, setLanguage] = useState('en')
const [loading, setLoading] = useState(false)
const messagesEndRef = useRef<HTMLDivElement>(null)
```

**Key Functions**:

`handleSendMessage()` - Form submission handler:
1. Prevent default form behavior
2. Check for empty input and loading state
3. Create user message object, add to state
4. Call backend with: message, language, and full history
5. Add assistant response to state
6. Handle errors with user-friendly message
7. Clear loading state

**Auto-scroll Effect**:
```typescript
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
}, [messages])
```

**Layout**:
- Header: Title + LanguageSelector
- Messages container: MessageBubble components + loading indicator
- Input footer: Text input + Send button

### File: `app/components/MessageBubble.tsx`

**Purpose**: Display individual messages with optional TTS playback (v2)

**Props**:
```typescript
interface Props {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  language?: string  // For TTS voice selection (v2)
}
```

**Styling**:
- User messages: Right-aligned, blue background (#007bff), white text
- Assistant messages: Left-aligned, light gray background (#e9ecef), dark text
- Timestamp: Small text below content
- Speaker button (v2): Shows 🔊 on hover, ⏳ while playing

**v2 Voice Features**:
- Speaker button on assistant messages only
- Calls `speakText(content, language)` on click
- Plays returned MP3 blob via native Audio API
- Shows loading state while fetching audio
- Error message if TTS fails

### File: `app/components/VoiceButton.tsx` (v2)

**Purpose**: Microphone recording button for speech-to-text input

**Props**:
```typescript
interface VoiceButtonProps {
  onTranscript: (text: string) => void
  disabled: boolean
}
```

**State Management**:
```typescript
const [recording, setRecording] = useState(false)
const [error, setError] = useState<string | null>(null)
const mediaRecorderRef = useRef<MediaRecorder | null>(null)
const audioChunksRef = useRef<Blob[]>([])
```

**Key Functions**:

`handleStartRecording()`:
1. Request microphone access via `navigator.mediaDevices.getUserMedia()`
2. Create MediaRecorder with audio/webm MIME type
3. Collect audio chunks via `ondataavailable` event
4. On `onstop`: send audio blob to `/voice/transcribe` endpoint
5. Call `onTranscript()` callback with transcribed text

`handleStopRecording()`:
1. Stop the MediaRecorder
2. Release microphone tracks
3. Set loading state to false

**Styling**:
- Idle: Blue button with mic emoji (🎤)
- Recording: Red button with stop emoji (⏹️)
- Disabled during chat loading
- Error messages shown below button in red text

**Error Handling**:
- NotAllowedError: User denied microphone permission
- NotFoundError: No microphone connected
- Generic errors logged to console with user-friendly message

### File: `app/components/LanguageSelector.tsx`

**Purpose**: Language selection dropdown

**Languages**:
```typescript
const LANGUAGES = [
  { code: 'en', label: '🇬🇧 English' },
  { code: 'fr', label: '🇫🇷 Français' },
  { code: 'vi', label: '🇻🇳 Tiếng Việt' },
]
```

**Behavior**:
- Button group showing all languages
- Active language button highlighted in blue with bold text
- Clicking button calls `onLanguageChange(code)`
- Future messages respond in selected language

### File: `lib/api.ts`

**Purpose**: API communication with backend

**sendMessage Function**:
```typescript
async function sendMessage(
  message: string,
  language: string,
  history: Message[]
): Promise<ChatResponse>
```

**Flow**:
1. Build request body: `{ message, language, history: formatted }`
2. Fetch to backend endpoint
3. Check response status (throw on 400+)
4. Parse JSON response
5. Return ChatResponse

**Error Handling**:
- Network errors: caught and logged
- HTTP errors: includes status code
- JSON parsing errors: caught

**transcribeAudio Function (v2)**:
```typescript
async function transcribeAudio(audioBlob: Blob): Promise<{ text: string }>
```

**Flow**:
1. Create FormData and append audio blob
2. POST to `/voice/transcribe` endpoint
3. Receive `{ text: "..." }` response
4. Return TranscribeResponse

**speakText Function (v2)**:
```typescript
async function speakText(text: string, language: string): Promise<Blob>
```

**Flow**:
1. POST to `/voice/speak` with `{ text, language }`
2. Receive MP3 audio blob from streaming response
3. Return blob for playback via `new Audio(URL.createObjectURL(blob))`

**v2 Error Handling**:
- Transcription errors: caught and shown in VoiceButton
- TTS errors: caught and shown in MessageBubble
- Network errors: user-friendly messages displayed

### File: `app/globals.css`

**Content**:
- CSS reset: Remove default margins, padding, set box-sizing
- Base styles: font family, line height, colors
- Body and html: height 100%, background colors

---

## Type Definitions

### Backend (Pydantic)

All backend data models use Pydantic for automatic validation:
- Required fields throw `ValidationError` if missing
- Type mismatches rejected at request boundary
- JSON serialization automatic with `.model_dump_json()`

### Frontend (TypeScript)

All frontend components use TypeScript interfaces:
- Props type-checked at compile time
- State types inferred from `useState()` initial value
- API response types match backend models

---

## Testing Guide

### Unit Testing Backend (Local)

**Test health endpoint**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

**Test chat endpoint with curl**:
```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "language": "en",
    "history": []
  }'
```

**Expected response**:
```json
{
  "content": "Hi there! How can I help you today?",
  "language": "en"
}
```

**Test language support**:
```bash
# Same request with language: "fr"
# Response should come in French
```

### Integration Testing (Local)

1. **Start both servers**:
   ```bash
   # Terminal 1 - Backend
   cd backend && uvicorn main:app --reload
   
   # Terminal 2 - Frontend
   cd frontend && npm run dev
   ```

2. **Open browser**: Navigate to `http://localhost:3000`

3. **Test scenarios (v1)**:
   - [ ] Page loads without errors
   - [ ] Input field is focused (autoFocus)
   - [ ] Send a simple message: "Hi"
   - [ ] Response arrives from GPT-4o
   - [ ] Message has timestamp
   - [ ] Switch language to French
   - [ ] Send message in French: "Bonjour"
   - [ ] Response is in French
   - [ ] Switch language to Vietnamese
   - [ ] Send message: "Xin chào"
   - [ ] Response is in Vietnamese
   - [ ] Test message history persists during session
   - [ ] Reload page - history should clear (v1 design)
   - [ ] Test with long message to verify scrolling

### Fact Caching Testing (v4.1)

**Unit Tests** (`backend/tests/test_fact_extractor.py`):
- Fact extraction from various message types
- Pattern matching for birthdays, preferences, contacts, work
- Multiple facts in single message
- Duplicate prevention
- Empty/invalid input handling

**Run tests**:
```bash
cd backend
pytest tests/test_fact_extractor.py -v
```

**Integration Tests** (`backend/tests/test_fact_manager.py`):
- Redis caching and retrieval
- TTL expiration behavior
- Owner vs Guest fact persistence
- Session isolation (facts don't leak between sessions)

**E2E Test** (`frontend/tests/test-fact-caching.js`):
Comprehensive Playwright test verifying:

**Owner Mode**:
- [ ] Login as owner (PIN 9999)
- [ ] Send: "My birthday is May 15"
- [ ] Bot remembers and responds with fact
- [ ] Send: "What is my birthday?" → Bot answers "May 15"
- [ ] Refresh page → Facts persist (24h cache + DB)

**Guest Mode**:
- [ ] Continue as guest (no auth)
- [ ] Send: "I like coffee"
- [ ] Bot remembers fact in conversation
- [ ] Send: "What do I like?" → Bot answers "coffee"
- [ ] Verify guest facts NOT visible in owner's session (isolation)

**Run E2E test**:
```bash
cd frontend/tests
node test-fact-caching.js
```

Expected output:
```
✅ ALL TESTS PASSED - Fact caching working correctly!

Owner Mode (24h Redis + Permanent DB):
  ✓ Facts extracted from messages
  ✓ Bot remembers birthday fact
  ✓ Bot remembers food preference
  ✓ Facts persist after page refresh

Guest Mode (1h Redis only):
  ✓ Facts extracted from messages
  ✓ Bot remembers coffee preference
  ✓ Bot remembers work location
  ✓ Facts NOT visible in other sessions
```

### Voice Integration Testing (v2)

1. **Microphone Recording**:
   - [ ] Click "Record" button
   - [ ] Browser prompts for microphone permission
   - [ ] Allow microphone access
   - [ ] Button shows "Stop Recording" in red
   - [ ] Speak into microphone
   - [ ] Click "Stop Recording"
   - [ ] Wait for transcription to complete
   - [ ] Transcribed text appears in input field
   - [ ] Text is editable before sending

2. **Text-to-Speech Playback**:
   - [ ] Send a message normally
   - [ ] Response appears with speaker icon (🔊)
   - [ ] Click speaker icon
   - [ ] Icon changes to hourglass (⏳)
   - [ ] Audio plays (you hear the message spoken)
   - [ ] Icon returns to speaker (🔊) when done
   - [ ] Click speaker again on same message
   - [ ] Audio plays again

3. **Voice with Multiple Languages**:
   - [ ] Record message in English, verify transcription
   - [ ] Switch language to French
   - [ ] Click speaker on a message - response in French
   - [ ] Switch to Vietnamese
   - [ ] Record message, verify transcription
   - [ ] Click speaker - response in Vietnamese

4. **Error Handling**:
   - [ ] Click record without microphone permission - error message
   - [ ] Try to record with network disconnected - error handling
   - [ ] Click speaker with network error - TTS error message shown

### Build Testing

**Backend**:
```bash
cd backend
pip install -r requirements.txt
python -m py_compile main.py config.py routers/chat.py
# No output = success
```

**Frontend**:
```bash
cd frontend
npm run build
# Should produce .next folder with no TypeScript errors
```

### Common Issues During Testing

**CORS Error**: 
- Frontend shows "error" in console
- Backend `FRONTEND_URL` doesn't match browser URL
- Fix: Update `.env` and restart server

**Message doesn't send**:
- Check backend is running: `curl http://localhost:8000/health`
- Check API URL in `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Check OpenAI API key is valid

**TypeScript compilation error**:
- Run `npm run build` to see full error
- Check component imports are correct
- Verify Props interfaces match usage

**"Cannot find module" error**:
- Run `npm install` in frontend directory
- Delete `node_modules` and `package-lock.json`, reinstall if persists

---

## Performance Considerations

### Backend
- Each request to GPT-4o takes 0.5-3 seconds depending on response length
- First request after deployment takes ~5 seconds (cold start on Railway)
- Subsequent requests use warm containers
- Memory usage: ~200MB base + API response processing

### Frontend
- Initial page load: 1-2 seconds (localhost) / 2-4 seconds (production)
- Message send-to-display: 0.5-3 seconds (network + OpenAI latency)
- Auto-scroll is smooth with `behavior: 'smooth'`
- No debouncing needed for input (form submission, not onChange)

### Optimizations (For Future)
- Message streaming (real-time token delivery)
- Frontend code splitting for faster initial load
- Request batching if multiple messages sent rapidly
- Caching previous responses (careful with language switching)

---
