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

### File: `config.py`

**Purpose**: Centralized settings management using Pydantic

**Key Code Sections**:
- `Settings` class inheriting from BaseSettings
- `OPENAI_API_KEY` (required) - fetched from `.env`
- `DEBUG` (optional, default False) - enables verbose logging
- `FRONTEND_URL` (optional, default localhost) - used for CORS

**How it works**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### File: `routers/chat.py`

**Purpose**: Chat message endpoint with OpenAI integration

**Data Models**:
```python
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    message: str
    language: str  # "en", "fr", "vi"
    history: List[Message]

class ChatResponse(BaseModel):
    content: str
    language: str
```

**POST /chat/message Endpoint**:
1. Receive `ChatRequest` with user message, language, and history
2. Build system prompt with language instruction
3. Convert history to OpenAI message format
4. Call `client.chat.completions.create(model="gpt-4o", temperature=0.7, messages=[...])`
5. Extract response content
6. Return `ChatResponse` with content and language

**System Prompt Template**:
```
You are a friendly and helpful AI assistant.
Always respond in {language}.
```

**Error Handling**:
- Missing message/language: Returns 400 error
- OpenAI API error: Returns 500 with error details
- Invalid history: Returns 400

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

**Purpose**: Display individual messages

**Props**:
```typescript
interface Props {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}
```

**Styling**:
- User messages: Right-aligned, blue background (#007bff), white text
- Assistant messages: Left-aligned, light gray background (#e9ecef), dark text
- Timestamp: Small text below content

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

3. **Test scenarios**:
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
