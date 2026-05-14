from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import DocumentChunk
from services.openai_client import embed_text
import uuid


async def store_chunk(
    db: Session,
    source_type: str,
    source_id: uuid.UUID,
    content: str
) -> DocumentChunk:
    """
    Embed text and store as a document chunk in pgvector.

    Args:
        db: Database session
        source_type: 'conversation', 'document', or 'fact'
        source_id: UUID of the source (message, document, or fact)
        content: Text content to embed

    Returns:
        Created DocumentChunk object
    """
    # Generate embedding
    embedding = await embed_text(content)

    # Create and store chunk
    chunk = DocumentChunk(
        source_type=source_type,
        source_id=source_id,
        content=content,
        embedding=embedding
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


async def retrieve_similar_chunks(
    db: Session,
    query_text: str,
    k: int = 5,
    threshold: float = 0.7
) -> list[DocumentChunk]:
    """
    Retrieve similar chunks from the vector store using cosine similarity.

    Args:
        db: Database session
        query_text: Query text to find similar chunks
        k: Number of results to return
        threshold: Minimum similarity score (0-1, cosine similarity)

    Returns:
        List of similar DocumentChunk objects, sorted by similarity
    """
    # Embed the query
    query_embedding = await embed_text(query_text)

    # Use PostgreSQL vector similarity search
    # Note: pgvector's cosine similarity returns distance, not similarity
    # Distance ranges from 0 (identical) to 2 (opposite)
    # Similarity = 1 - distance / 2
    stmt = select(DocumentChunk).order_by(
        DocumentChunk.embedding.cosine_distance(query_embedding)
    ).limit(k)

    results = db.execute(stmt).scalars().all()

    # Filter by threshold if needed
    # For now, just return top k results
    return list(results)


async def upsert_message_chunk(
    db: Session,
    message_id: uuid.UUID,
    content: str
) -> DocumentChunk:
    """Store a message as a chunk for RAG retrieval."""
    # Delete existing chunk if present (for updates)
    db.query(DocumentChunk).filter(
        DocumentChunk.source_type == "conversation",
        DocumentChunk.source_id == message_id
    ).delete()
    db.commit()

    # Store new chunk
    return await store_chunk(db, "conversation", message_id, content)


async def bulk_retrieve_facts(
    db: Session,
    query_text: str,
    k: int = 3
) -> list[str]:
    """Retrieve personal facts relevant to the query."""
    chunks = await retrieve_similar_chunks(db, query_text, k=k)
    return [chunk.content for chunk in chunks]
