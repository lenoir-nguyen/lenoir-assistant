# Python/FastAPI Coding Standards

## Project Structure

```
backend/
├── main.py                 # App factory, CORS, routers
├── config.py              # Pydantic Settings
├── routers/
│   ├── __init__.py
│   ├── chat.py            # /chat/* endpoints
│   ├── auth.py            # /auth/* endpoints
│   └── voice.py           # /voice/* endpoints
├── services/              # Business logic
│   ├── identity.py        # Auth helpers
│   ├── openai_client.py   # OpenAI wrappers
│   └── chain.py           # LangChain builders
├── db/
│   ├── models.py          # SQLAlchemy models
│   ├── session.py         # Database connection
│   └── utils.py           # Query helpers
└── tests/
    ├── test_auth.py
    ├── test_chat.py
    └── test_voice.py
```

## Router Pattern

```python
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    language: str = "en"

class ChatResponse(BaseModel):
    content: str
    language: str

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest, http_request: Request):
    """
    Docstring describes the endpoint purpose and behavior.
    
    Args:
        request: ChatRequest with message and language
        http_request: FastAPI Request object for headers
    
    Returns:
        ChatResponse with content and language
    
    Raises:
        HTTPException(422): Validation error
        HTTPException(500): Server error
    """
    # Implementation
    return ChatResponse(content="...", language=request.language)
```

## Error Handling

```python
# Always use HTTPException for API errors
from fastapi import HTTPException

# Bad request
if not request.message.strip():
    raise HTTPException(status_code=400, detail="Message cannot be empty")

# Not found
if not session:
    raise HTTPException(status_code=404, detail="Session not found")

# Server error
try:
    response = client.chat.completions.create(...)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

## Async/Await Pattern

```python
# Always async in FastAPI
async def database_operation():
    async with db_session() as session:
        result = await session.execute(query)
        return result.scalars().first()

# Dependency injection with async
async def get_current_user(request: Request) -> User:
    token = request.headers.get("Authorization")
    # async operations here
    return user
```

## Environment Variables

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str  # Required
    DEBUG: bool = False   # Optional with default
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# In routers
def router():
    api_key = settings.OPENAI_API_KEY
```

## Database Query Pattern

```python
from sqlalchemy import select
from db.models import Session as SessionModel
from db.session import get_db

# In endpoint
async def chat_message(..., db: AsyncSession = Depends(get_db)):
    # Query using SQLAlchemy async pattern
    stmt = select(SessionModel).filter(SessionModel.id == session_id)
    result = await db.execute(stmt)
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Insert
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
```

## Testing Pattern (pytest)

```python
# tests/test_chat.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_chat_message_success():
    response = client.post(
        "/chat/message",
        json={"message": "Hello", "language": "en"}
    )
    assert response.status_code == 200
    assert "content" in response.json()

def test_chat_message_missing_fields():
    response = client.post(
        "/chat/message",
        json={"language": "en"}  # Missing message
    )
    assert response.status_code == 422  # Pydantic validation error
```

## Naming Conventions

- **Routers**: `{domain}.py` (auth.py, chat.py, voice.py)
- **Services**: `{service_name}.py` (identity.py, openai_client.py)
- **Models**: `{Entity}` class (ChatRequest, ChatResponse)
- **Endpoints**: kebab-case in path (`/auth/login`, `/chat/message`)
- **Variables**: snake_case (`session_id`, `api_key`)
- **Constants**: UPPER_SNAKE_CASE (`SUPPORTED_LANGUAGES`)

## Type Hints

Always use type hints:

```python
# Good
async def get_session(session_id: UUID) -> SessionModel | None:
    ...

def format_prompt(template: str, language: str) -> str:
    return template.format(language=language)

# Avoid
def get_session(session_id):  # Missing types
    ...
```

## Comments

Minimal comments; code should be self-explanatory:

```python
# Good - self-explanatory names
messages = await get_recent_messages(session_id, limit=10)

# Avoid - unnecessary comment
# Get messages
messages = await get_recent_messages(session_id, limit=10)

# Good - explain WHY, not WHAT
# Limit to 10 messages to fit in LangChain token budget
messages = await get_recent_messages(session_id, limit=10)
```

## Import Organization

```python
# Standard library
import json
from datetime import datetime
from typing import Optional

# Third-party
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from openai import OpenAI

# Local
from config import get_settings
from db.models import Session
from services.identity import verify_pin
```
