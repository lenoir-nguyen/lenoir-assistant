"""
Chat router for handling conversation endpoints (v4: LangChain + PostgreSQL).

This module implements persistent chat with:
- LangChain ConversationChain for intelligent memory management
- PostgreSQL database for conversation persistence (owner only)
- Async SQLAlchemy for non-blocking database operations
- Multi-language support with language persistence
- Owner vs guest differentiation (owner: persistent, guest: ephemeral)

Database Flow:
1. Each chat request gets or creates a Session in PostgreSQL
2. Backend fetches previous messages from DB for LangChain memory
3. LangChain ConversationChain manages prompt building + OpenAI
4. Backend stores user message and assistant response in DB
5. Frontend receives session_id to persist across page reloads
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from config import get_settings
from db.session import get_db
from db.utils import get_or_create_session, get_recent_messages, store_message
from routers.auth import get_is_owner
from services.chain import build_owner_chain, build_stranger_chain

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


# ============================================================================
# Data Models
# ============================================================================

class Message(BaseModel):
    """Represents a single message in conversation history."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Request payload for /chat/message endpoint (v4)."""
    message: str
    language: str = "en"
    history: list[Message] = []  # Deprecated in v4 (backend fetches from DB)
    session_id: str | None = None  # NEW: session UUID for persistence


class ChatResponse(BaseModel):
    """Response payload from /chat/message endpoint (v4)."""
    content: str
    language: str
    session_id: str  # NEW: return session_id so frontend can persist it


# ============================================================================
# Chat Endpoint (v4: LangChain + Database)
# ============================================================================

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle chat message with LangChain orchestration and database persistence.

    v4 Workflow:
    1. Check if user is authenticated as owner (bearer token from v3)
    2. Get or create session in PostgreSQL
    3. Store user message in database
    4. Fetch recent messages from database for LangChain memory
    5. Build appropriate LangChain chain (owner vs guest)
    6. Call LangChain ConversationChain (orchestrates OpenAI call)
    7. Store assistant response in database
    8. Return response + session_id (for frontend persistence)

    Args:
        request: ChatRequest with message, language, session_id
        http_request: FastAPI Request (reads Authorization header for owner check)
        db: AsyncSession from Depends(get_db)

    Returns:
        ChatResponse with content, language, session_id

    Raises:
        HTTPException: 500 if database or OpenAI fails
    """
    try:
        # Step 1: Check if user is authenticated as owner
        is_owner = await get_is_owner(http_request)

        # Step 2: Parse session_id (UUID or None)
        session_id = None
        if request.session_id:
            try:
                session_id = UUID(request.session_id)
            except ValueError:
                session_id = None

        # Step 3: Get or create session in PostgreSQL
        db_session = await get_or_create_session(
            db=db,
            session_id=session_id,
            is_owner=is_owner,
            language=request.language
        )
        session_id = db_session.id

        # Step 4: Store user message in database
        await store_message(
            db=db,
            session_id=session_id,
            role="user",
            content=request.message,
            language=request.language,
            modality="text"
        )

        # Step 5: Fetch recent messages for LangChain memory
        # Owner: 10 messages, Guest: 5 messages
        limit = 10 if is_owner else 5
        recent_messages = await get_recent_messages(db, session_id, limit=limit)

        # Step 6: Build LangChain chain (owner vs guest)
        if is_owner:
            chain, llm = build_owner_chain(db, request.language)
        else:
            chain, llm = build_stranger_chain(request.language)

        # Step 7: Load memory with recent messages (exclude current user message)
        for msg in recent_messages:
            if msg.role == "user":
                chain.memory.chat_memory.add_user_message(msg.content)
            else:
                chain.memory.chat_memory.add_ai_message(msg.content)

        # Step 8: Call LangChain ConversationChain
        # This orchestrates: prompt building + OpenAI API call + memory update
        response = await chain.apredict(input=request.message)

        # Step 9: Store assistant response in database
        await store_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=response,
            language=request.language,
            modality="text"
        )

        # Step 10: Return response with session_id for frontend persistence
        return ChatResponse(
            content=response,
            language=request.language,
            session_id=str(session_id)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
