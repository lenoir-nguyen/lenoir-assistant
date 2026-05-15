# Reusable Skills & Patterns from Lenoir Chatbot

This document extracts architectural patterns, code patterns, and implementation strategies from Lenoir Chatbot that can be reused in other projects.

---

## 🏗️ Architectural Patterns

### 1. Dual-Mode Application Pattern

**Pattern**: Build application with two distinct operational modes (owner/authenticated vs. guest/public).

**Implementation**:
```python
# backend/routers/chat.py
if session.is_owner:
    # Owner mode: full features
    chain = build_owner_chain(db, language)
    facts = retrieve_relevant_facts(db, query)
    augmented_prompt = f"{context}\n{query}"
else:
    # Guest mode: limited features
    chain = build_stranger_chain(language)
    augmented_prompt = query  # No context injection
```

**Use Cases**:
- Public vs. private chat applications
- Free tier vs. premium tier features
- Anonymous vs. authenticated user experiences
- Guest checkout vs. full account features

**Reusability**: Replace "owner/stranger" with any two-mode concept (admin/user, paid/free, pro/lite)

---

### 2. Real-Time Streaming Pattern (SSE)

**Pattern**: Stream response tokens to client using Server-Sent Events for real-time feedback.

**Implementation**:
```python
# backend/routers/chat.py - Streaming Response
@router.post("/message", response_class=StreamingResponse)
async def chat_message(request: ChatRequest):
    async def generate():
        # Stream tokens one by one
        response = await chain.apredict(input=prompt)
        for token in response.split():
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
```

**Frontend Handler**:
```typescript
// frontend/lib/api.ts
const response = await fetch(`${API_URL}/chat/message`, {method: 'POST'});
const reader = response.body?.getReader();
while (true) {
    const { done, value } = await reader?.read() ?? {};
    if (done) break;
    const text = new TextDecoder().decode(value);
    // Parse SSE format and update UI
}
```

**Use Cases**:
- Real-time chat applications
- Live API response streaming
- Progress indication (generation, processing)
- WebSocket-free real-time communication

**Advantages**:
- HTTP/1.1 compatible (no special WebSocket protocol)
- Automatic reconnection
- Simple text-based format
- Works in all modern browsers

---

### 3. RAG (Retrieval-Augmented Generation) Pattern

**Pattern**: Enhance LLM responses with retrieved context before generation.

**Implementation**:
```python
# 1. Store embeddings
async def store_chunk(db, source_type, source_id, content):
    embedding = await embed_text(content)  # OpenAI API
    chunk = DocumentChunk(
        source_type=source_type,
        source_id=source_id,
        embedding=embedding,
        content=content
    )
    db.add(chunk)
    db.commit()

# 2. Retrieve similar chunks
async def retrieve_similar_chunks(db, query_text, k=5):
    query_embedding = await embed_text(query_text)
    results = db.query(DocumentChunk).order_by(
        DocumentChunk.embedding.cosine_distance(query_embedding)
    ).limit(k).all()
    return results

# 3. Augment prompt with context
facts = await retrieve_similar_chunks(db, user_query)
context = "\n".join([f"- {fact.content}" for fact in facts])
augmented_prompt = f"Context:\n{context}\n\nQuery: {user_query}"
response = await llm.generate(augmented_prompt)
```

**Use Cases**:
- Document question-answering (PDF/website Q&A)
- Personalized AI assistants (customer data retrieval)
- Knowledge base integration
- Long-context AI responses (beyond token limit)

**Vector Database Options**:
- pgvector (Postgres extension) — Co-located with relational data
- Pinecone — Serverless vector search
- Weaviate — Open-source vector DB
- Supabase (pgvector) — Managed PostgreSQL with pgvector

---

### 4. Session-Based Memory Pattern

**Pattern**: Maintain separate memory buffers per user session for context management.

**Implementation**:
```python
# backend/services/chain.py
def build_owner_chain(db: Session, language: str = "en"):
    # Large memory: store conversation for context
    memory = ConversationBufferWindowMemory(k=10)
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    return chain

def build_stranger_chain(language: str = "en"):
    # Small memory: forget after conversation
    memory = ConversationBufferWindowMemory(k=5)
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    return chain
```

**Use Cases**:
- Multi-user chatbots
- Conversation history management
- Context-aware responses
- Memory isolation between users

**Memory Types** (LangChain):
- `ConversationBufferWindowMemory` — Keep last N messages
- `ConversationBufferMemory` — Keep all messages
- `ConversationSummaryMemory` — Summarize old messages
- `ConversationTokenBufferMemory` — Keep last N tokens

---

## 💻 Code Patterns

### 1. Async Database Operations

**Pattern**: Use SQLAlchemy with async sessions for non-blocking database I/O.

**Implementation**:
```python
# backend/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# backend/routers/chat.py
@router.post("/message")
async def chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    session = await db.get(SessionModel, session_id)  # Non-blocking query
    await db.commit()
```

**Benefits**:
- Non-blocking I/O (handle more concurrent users)
- Better resource utilization
- Faster response times under load

---

### 2. Pydantic Settings from Environment

**Pattern**: Use Pydantic to validate and type-check environment variables at startup.

**Implementation**:
```python
# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    OWNER_PIN_HASH: str
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()  # Auto-validates on startup
```

**Benefits**:
- Type validation at startup (fail fast)
- Clear documentation of required variables
- Fallback default values
- Automatic .env file loading

---

### 3. API Response Models (Pydantic)

**Pattern**: Define request/response schemas with Pydantic for auto-documentation and validation.

**Implementation**:
```python
# backend/routers/chat.py
class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"

class ChatResponse(BaseModel):
    message_id: str
    role: str  # "user" or "assistant"
    content: str
    modality: str = "text"

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    # FastAPI auto-validates request, serializes response
    ...
```

**Benefits**:
- Auto-generated OpenAPI documentation
- Request validation at API boundary
- Type hints in IDE
- Runtime type checking

---

### 4. Dependency Injection (FastAPI)

**Pattern**: Use FastAPI `Depends()` for dependency injection (e.g., database sessions).

**Implementation**:
```python
# backend/db/session.py
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# backend/routers/chat.py
@router.post("/message")
async def chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db)  # Injected by FastAPI
):
    # db is automatically provided and cleaned up
    session = db.query(SessionModel).filter(...).first()
```

**Benefits**:
- Automatic resource cleanup
- Testable (easy to mock dependencies)
- Readable, explicit dependencies
- Avoids global state

---

### 5. Vector Embedding & Search (pgvector)

**Pattern**: Store and search embeddings using pgvector PostgreSQL extension.

**Implementation**:
```python
# backend/db/models.py
from pgvector.sqlalchemy import Vector

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(UUID, primary_key=True)
    embedding = Column(Vector(1536))  # OpenAI embedding dimension
    content = Column(String)

# backend/services/vectorstore.py
async def retrieve_similar_chunks(db, query_text, k=5):
    query_embedding = await embed_text(query_text)
    
    # Cosine distance search via pgvector
    results = db.query(DocumentChunk).order_by(
        DocumentChunk.embedding.cosine_distance(query_embedding)
    ).limit(k).all()
    
    return results
```

**Distance Metrics** (pgvector):
- `cosine_distance()` — Cosine distance (0 = identical, 2 = opposite)
- `l2_distance()` — Euclidean distance
- `inner_product()` — Inner product (dot product)

**Index Types** (pgvector):
- `ivfflat` — Fast approximate search (default, recommended)
- `hnsw` — Hierarchical navigable small-world
- No index — Exact search (slow on large datasets)

---

### 6. Bcrypt Password Hashing

**Pattern**: Securely hash passwords/PINs using bcrypt with configurable cost factor.

**Implementation**:
```python
# backend/services/identity.py
import bcrypt

def hash_pin(pin: str) -> str:
    """Generate bcrypt hash (setup only)"""
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds = ~100ms hash time
    return bcrypt.hashpw(pin.encode('utf-8'), salt).decode('utf-8')

def verify_pin(provided_pin: str, hash_from_env: str) -> bool:
    """Verify PIN against stored hash (no plain-text comparison)"""
    return bcrypt.checkpw(
        provided_pin.encode('utf-8'),
        hash_from_env.encode('utf-8')
    )
```

**Cost Factor Recommendations**:
- `rounds=4-6` — Tests, demos (milliseconds)
- `rounds=10-12` — Production (100ms, GPU-resistant)
- `rounds=14+` — High-security (seconds, overkill for most apps)

**Why Bcrypt?**
- Built-in salt (no separate salt management)
- Configurable cost factor (scales with hardware)
- GPU/ASIC resistant (good against brute-force)
- Widely supported (Python, Node, Go, Rust, etc.)

---

### 7. LangChain Chain Composition

**Pattern**: Build modular chains that can be easily swapped or extended.

**Implementation**:
```python
# backend/services/chain.py
def build_chain(language: str, use_rag: bool = True):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7, streaming=True)
    memory = ConversationBufferWindowMemory(k=10)
    
    system_prompt = f"Respond in {language}"
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    chain = LLMChain(llm=llm, prompt=chat_prompt, memory=memory)
    return chain
```

**Easy Modifications**:
- Swap `ChatOpenAI` → `ChatAnthropic` (different LLM)
- Change `temperature` (creativity level)
- Swap memory type (buffer → summary)
- Add retriever (for RAG)

---

## 🔌 Integration Patterns

### 1. OpenAI API Integration

**Pattern**: Async wrapper functions for OpenAI API calls with error handling.

**Implementation**:
```python
# backend/services/openai_client.py
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    """Speech-to-text via Whisper API"""
    transcript = await client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.webm", audio_bytes),
        language=language
    )
    return transcript.text

async def synthesize_speech(text: str, language: str = "en") -> bytes:
    """Text-to-speech via OpenAI TTS API"""
    speech = await client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
        language=language
    )
    return speech.content

async def embed_text(text: str) -> list[float]:
    """Generate embeddings via OpenAI Embeddings API"""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        dimensions=1536
    )
    return response.data[0].embedding
```

**Benefits**:
- Centralized API key management
- Async/await (non-blocking)
- Consistent error handling
- Easy to test (mock these functions)

---

### 2. Frontend-Backend Communication (Axios)

**Pattern**: Centralized API client with consistent error handling and request formatting.

**Implementation**:
```typescript
// frontend/lib/api.ts
import axios from 'axios';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    headers: { 'Content-Type': 'application/json' }
});

// Chat streaming
export async function* chatMessage(request: ChatRequest) {
    const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        body: JSON.stringify(request)
    });
    
    const reader = response.body?.getReader();
    while (true) {
        const { done, value } = await reader?.read() ?? {};
        if (done) break;
        
        const text = new TextDecoder().decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const json = JSON.parse(line.slice(6));
                yield json;
            }
        }
    }
}

// Regular endpoints
export async function verifyPin(sessionId: string, pin: string) {
    const response = await api.post('/auth/verify-pin', {
        session_id: sessionId,
        pin: pin
    });
    return response.data;
}
```

**Benefits**:
- Centralized configuration
- Consistent error handling
- Interceptors for auth, logging, etc.
- Type-safe with TypeScript

---

## 📱 Frontend Patterns

### 1. Conditional Rendering (Auth State)

**Pattern**: Show different UI based on authentication state.

**Implementation**:
```typescript
// frontend/app/page.tsx
const [isOwner, setIsOwner] = useState<boolean | null>(null);

useEffect(() => {
    healthCheck().then(() => {
        // Create session (owner will be determined during auth)
        setIsOwner(false);  // Default: stranger
    });
}, []);

return (
    <>
        {isOwner === null ? (
            <div>Loading...</div>
        ) : isOwner === false ? (
            <IdentityPrompt onAuthenticated={setIsOwner} />
        ) : (
            <ChatWindow isOwner={true} />
        )}
    </>
);
```

**Benefits**:
- Clean separation of concerns
- Easy to understand flow
- Testable (unit test each component)

---

### 2. Browser MediaRecorder for Voice

**Pattern**: Capture audio from browser microphone using native MediaRecorder API.

**Implementation**:
```typescript
// frontend/app/components/VoiceButton.tsx
const [isRecording, setIsRecording] = useState(false);
let mediaRecorder: MediaRecorder;

const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
    });
    
    const chunks: Blob[] = [];
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        const transcript = await transcribeAudio(audioBlob, sessionId, language);
        setInputText(transcript);  // Fill text field
    };
    
    mediaRecorder.start();
    setIsRecording(true);
};

const stopRecording = () => {
    mediaRecorder.stop();
    setIsRecording(false);
};
```

**Benefits**:
- No external libraries needed
- Works in all modern browsers
- Requires user permission (privacy-first)
- Compressed audio format (opus)

---

### 3. Streaming Response Handling

**Pattern**: Display tokens as they arrive from SSE stream.

**Implementation**:
```typescript
// frontend/lib/api.ts
async function* streamChat(request: ChatRequest) {
    const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
    });
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader?.read() ?? {};
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                yield data;
            }
        }
    }
}

// frontend/app/components/ChatWindow.tsx
const handleSendMessage = async () => {
    let fullResponse = '';
    
    for await (const event of streamChat({ session_id, message, language })) {
        if (event.token) {
            fullResponse += event.token + ' ';
            setMessages([...messages, { role: 'assistant', content: fullResponse }]);
        }
    }
};
```

**Benefits**:
- Real-time visual feedback
- Better UX (not waiting for full response)
- Works with SSE (no WebSocket needed)

---

## 🔐 Security Patterns

### 1. Environment Variables for Secrets

**Pattern**: Never hardcode secrets; always use environment variables.

**Implementation**:
```python
# backend/config.py
class Settings(BaseSettings):
    OPENAI_API_KEY: str  # Required from .env
    OWNER_PIN_HASH: str  # Required from .env
    DATABASE_URL: str    # Required from .env
    
    class Config:
        env_file = ".env"
```

```bash
# .env (git-ignored)
OPENAI_API_KEY=sk-proj-xxx
OWNER_PIN_HASH=$2b$12$xxx
DATABASE_URL=postgresql://user:pass@localhost/db
```

**Benefits**:
- Secrets never in code repository
- Easy to rotate (update .env)
- Different secrets per environment (dev, staging, prod)

---

### 2. CORS Configuration

**Pattern**: Restrict API access to specific frontend URLs.

**Implementation**:
```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local dev
        settings.FRONTEND_URL      # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Benefits**:
- Prevents cross-origin attacks
- Whitelist known frontend domains
- Protects API from CSRF attacks

---

### 3. Input Validation

**Pattern**: Validate all user input at API boundary using Pydantic.

**Implementation**:
```python
# backend/routers/chat.py
class ChatRequest(BaseModel):
    session_id: str  # Must be valid UUID
    message: str     # Must be non-empty
    language: str = "en"  # Must be en/fr/vi (add validator)
    
    @field_validator('message')
    def message_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        return v.strip()
    
    @field_validator('language')
    def language_valid(cls, v):
        if v not in ['en', 'fr', 'vi']:
            raise ValueError('Invalid language code')
        return v
```

**Benefits**:
- Prevents SQL injection (via ORM + validation)
- Prevents XSS (validation + output escaping)
- Clear error messages to client

---

## 📚 Extension Points

These patterns can be extended:

1. **Add new languages**: Add to language validator, update system prompts
2. **Change LLM**: Swap `ChatOpenAI` → `ChatAnthropic` in chain.py
3. **Add authentication**: Extend identity service with email/OAuth
4. **Store history differently**: Change database backend (SQLite, MongoDB)
5. **Use different embeddings**: Swap embedding model in openai_client.py
6. **Add file uploads**: Extend memory router with document parsing

---

## 🎯 Summary

Reusable patterns from Lenoir Chatbot:
- Dual-mode applications (owner/guest, paid/free, etc.)
- Real-time streaming (SSE, WebSockets)
- RAG system architecture
- Session-based memory management
- Async database operations
- Pydantic models for validation
- Dependency injection (FastAPI)
- Vector search with pgvector
- Bcrypt hashing
- LangChain composition
- OpenAI API integration
- Frontend-backend communication
- Voice/media handling
- Security best practices

**Each pattern is production-tested and can be adapted to other projects.**

