"""
Database utility functions for v4 persistent conversation storage.

Provides helpers for session management, message retrieval, and storage.
Used by routers/chat.py to abstract database operations.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from db.models import Session as SessionModel, Message, PersonalFact
from services.fact_extractor import Fact


async def get_or_create_session(
    db: AsyncSession,
    session_id: UUID | None,
    is_owner: bool,
    language: str = "en"
) -> SessionModel:
    """
    Fetch existing session from DB or create a new one.

    Args:
        db: Async database session
        session_id: UUID of session (generates new if None)
        is_owner: Whether user is authenticated as owner
        language: User's preferred language (en, fr, vi)

    Returns:
        SessionModel instance (fetched or newly created)
    """
    import uuid

    if not session_id:
        session_id = uuid.uuid4()

    # Try to fetch existing session
    stmt = select(SessionModel).filter(SessionModel.id == session_id)
    result = await db.execute(stmt)
    session = result.scalars().first()

    if not session:
        # Create new session if doesn't exist
        session = SessionModel(
            id=session_id,
            is_owner=is_owner,
            language=language,
            created_at=datetime.utcnow()
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    return session


async def get_recent_messages(
    db: AsyncSession,
    session_id: UUID,
    limit: int = 10
) -> list[Message]:
    """
    Fetch recent messages from a session, in chronological order.

    Args:
        db: Async database session
        session_id: UUID of session
        limit: Max messages to return (default 10 for owners, 5 for guests)

    Returns:
        List of Message objects in chronological order (oldest first)
    """
    stmt = (
        select(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    # Reverse to get chronological order (oldest first)
    return list(reversed(messages))


async def store_message(
    db: AsyncSession,
    session_id: UUID,
    role: str,
    content: str,
    language: str = "en",
    modality: str = "text"
) -> Message:
    """
    Store a message in the database.

    Args:
        db: Async database session
        session_id: UUID of session
        role: "user" or "assistant"
        content: Message text
        language: Message language (default "en")
        modality: "text" or "voice" (default "text")

    Returns:
        Newly created Message object
    """
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        language=language,
        modality=modality,
        created_at=datetime.utcnow()
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def store_personal_fact(
    db: AsyncSession,
    fact: Fact
) -> PersonalFact:
    """
    Store a personal fact in the database (v4.1 long-term memory for owners).

    Args:
        db: Async database session
        fact: Fact object with category, content, etc.

    Returns:
        Newly created PersonalFact object
    """
    personal_fact = PersonalFact(
        category=fact.category,
        content=fact.content,
        created_at=datetime.utcnow()
    )
    db.add(personal_fact)
    await db.commit()
    await db.refresh(personal_fact)
    return personal_fact
