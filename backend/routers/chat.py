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
from langchain_core.messages import AIMessage, HumanMessage
from uuid import UUID, uuid4
from config import get_settings
from db.session import get_db
from db.utils import get_or_create_session, get_recent_messages, store_message
from routers.auth import get_is_owner
from services.chain import (
    get_llm,
    build_owner_system_prompt,
    build_stranger_system_prompt,
    build_owner_chain_response,
    build_stranger_chain_response,
)

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

        # Step 5: Fetch recent messages for context
        # Owner: 10 messages, Guest: 5 messages
        limit = 10 if is_owner else 5
        recent_messages = await get_recent_messages(db, session_id, limit=limit)

        # Step 6: Get LLM instance
        llm = get_llm()

        # Step 7: Convert database messages to LangChain format
        langchain_messages = []
        for msg in recent_messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))

        # Step 8: Build system prompt and call LLM
        if is_owner:
            system_prompt = build_owner_system_prompt(request.language)
            response = await build_owner_chain_response(
                llm, system_prompt, langchain_messages, request.message
            )
        else:
            system_prompt = build_stranger_system_prompt(request.language)
            response = await build_stranger_chain_response(
                llm, system_prompt, langchain_messages, request.message
            )

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


@router.get("/history/{session_id}", response_model=list[Message])
async def get_chat_history(
    session_id: str,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch chat history for a session (v4: Fetch from PostgreSQL).

    This endpoint allows the frontend to retrieve all stored messages
    for a session after a page refresh. Messages are returned in
    chronological order (oldest first).

    Args:
        session_id: UUID of the session to fetch history for
        http_request: FastAPI Request (for potential future auth checks)
        db: AsyncSession from Depends(get_db)

    Returns:
        list[Message]: List of messages in chronological order

    Raises:
        HTTPException: 400 if session_id is invalid UUID
                      500 if database query fails
    """
    try:
        # Parse session_id to UUID
        session_id_uuid = UUID(session_id)

        # Fetch up to 50 messages from this session
        messages = await get_recent_messages(db, session_id_uuid, limit=50)

        # Convert database models to Pydantic Message models
        return [Message(role=msg.role, content=msg.content) for msg in messages]

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
