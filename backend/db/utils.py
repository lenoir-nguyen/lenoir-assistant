"""
Database utility functions for v4+ persistent conversation storage and v5 RAG.

Provides helpers for:
- Session management (v4)
- Message retrieval and storage (v4)
- Fact persistence (v4.1)
- Document management (v5)

Used by routers to abstract database operations.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
from db.models import Session as SessionModel, Message, PersonalFact, Document, DocumentChunk
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


# ============================================================================
# Document Management Utilities (v5 RAG)
# ============================================================================

async def get_document_by_id(
    db: AsyncSession,
    document_id: UUID
) -> Document | None:
    """
    Fetch a document by ID.

    Args:
        db: Async database session
        document_id: UUID of document

    Returns:
        Document object or None if not found
    """
    stmt = select(Document).filter(Document.id == document_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_all_documents(db: AsyncSession) -> list[Document]:
    """
    Get all documents, ordered by upload date (newest first).

    Args:
        db: Async database session

    Returns:
        List of all Document objects
    """
    stmt = select(Document).order_by(Document.uploaded_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_document_chunks(
    db: AsyncSession,
    document_id: UUID
) -> list[DocumentChunk]:
    """
    Get all chunks for a specific document.

    Args:
        db: Async database session
        document_id: UUID of document

    Returns:
        List of DocumentChunk objects for this document
    """
    stmt = (
        select(DocumentChunk)
        .filter(
            DocumentChunk.source_type == 'document',
            DocumentChunk.source_id == document_id
        )
        .order_by(DocumentChunk.created_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_document_chunk_count(
    db: AsyncSession,
    document_id: UUID
) -> int:
    """
    Get the number of chunks for a document.

    Args:
        db: Async database session
        document_id: UUID of document

    Returns:
        Number of chunks
    """
    stmt = (
        select(DocumentChunk)
        .filter(
            DocumentChunk.source_type == 'document',
            DocumentChunk.source_id == document_id
        )
    )
    result = await db.execute(stmt)
    return len(result.scalars().all())


async def delete_document_and_chunks(
    db: AsyncSession,
    document_id: UUID
) -> int:
    """
    Delete a document and cascade-delete all associated chunks.

    Args:
        db: Async database session
        document_id: UUID of document to delete

    Returns:
        Number of chunks deleted

    Raises:
        ValueError: If document not found
    """
    # Get document to verify it exists
    document = await get_document_by_id(db, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")

    # Delete all chunks for this document
    chunk_stmt = delete(DocumentChunk).filter(
        DocumentChunk.source_type == 'document',
        DocumentChunk.source_id == document_id
    )
    chunk_result = await db.execute(chunk_stmt)
    chunk_count = chunk_result.rowcount

    # Delete document
    doc_stmt = delete(Document).filter(Document.id == document_id)
    await db.execute(doc_stmt)
    await db.commit()

    return chunk_count
