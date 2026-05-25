"""
Integration tests for RAG flow (v5 feature).

Tests document upload, chunking, embedding, semantic search, and LLM context injection.
"""

import pytest
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from db.models import Base, Document, DocumentChunk
from db.utils import (
    get_all_documents,
    get_document_chunks,
    delete_document_and_chunks,
    get_document_chunk_count,
)
from services.rag_formatter import format_chunks_for_context, format_chunks_for_citation
from uuid import uuid4


class TestRAGFlow:
    """Test the complete RAG flow from document to LLM context."""

    @pytest.fixture
    async def db(self):
        """Create an in-memory SQLite database for testing."""
        # Use SQLite for testing (supports basic SQLAlchemy features)
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            yield session

        await engine.dispose()

    @pytest.mark.asyncio
    async def test_document_storage_and_retrieval(self, db):
        """Test storing and retrieving a document."""
        doc_id = uuid4()
        doc = Document(
            id=doc_id,
            filename="test.txt",
            description="Test document",
            uploaded_at="2026-05-25T00:00:00Z",
        )
        db.add(doc)
        await db.commit()

        # Retrieve the document
        retrieved = await get_all_documents(db)
        assert len(retrieved) == 1
        assert retrieved[0].filename == "test.txt"

    @pytest.mark.asyncio
    async def test_chunk_storage_and_retrieval(self, db):
        """Test storing and retrieving document chunks."""
        doc_id = uuid4()
        doc = Document(
            id=doc_id,
            filename="test.txt",
            description="Test",
            uploaded_at="2026-05-25T00:00:00Z",
        )
        db.add(doc)
        await db.commit()

        # Add chunks
        chunk1 = DocumentChunk(
            id=uuid4(),
            source_type="document",
            source_id=doc_id,
            content="First chunk content with relevant information",
            embedding=[0.1] * 1536,  # Mock embedding
        )
        chunk2 = DocumentChunk(
            id=uuid4(),
            source_type="document",
            source_id=doc_id,
            content="Second chunk with more data",
            embedding=[0.2] * 1536,
        )
        db.add(chunk1)
        db.add(chunk2)
        await db.commit()

        # Retrieve chunks
        chunks = await get_document_chunks(db, doc_id)
        assert len(chunks) == 2
        assert all("chunk" in c.content.lower() for c in chunks)

    @pytest.mark.asyncio
    async def test_chunk_count(self, db):
        """Test counting chunks for a document."""
        doc_id = uuid4()
        doc = Document(
            id=doc_id,
            filename="test.txt",
            description="Test",
            uploaded_at="2026-05-25T00:00:00Z",
        )
        db.add(doc)
        await db.commit()

        # Add 3 chunks
        for i in range(3):
            chunk = DocumentChunk(
                id=uuid4(),
                source_type="document",
                source_id=doc_id,
                content=f"Chunk {i} content",
                embedding=[0.1] * 1536,
            )
            db.add(chunk)
        await db.commit()

        # Get count
        count = await get_document_chunk_count(db, doc_id)
        assert count == 3

    @pytest.mark.asyncio
    async def test_delete_document_cascades_chunks(self, db):
        """Test that deleting a document also deletes its chunks."""
        doc_id = uuid4()
        doc = Document(
            id=doc_id,
            filename="test.txt",
            description="Test",
            uploaded_at="2026-05-25T00:00:00Z",
        )
        db.add(doc)
        await db.commit()

        # Add chunks
        for i in range(2):
            chunk = DocumentChunk(
                id=uuid4(),
                source_type="document",
                source_id=doc_id,
                content=f"Chunk {i}",
                embedding=[0.1] * 1536,
            )
            db.add(chunk)
        await db.commit()

        # Verify chunks exist
        count_before = await get_document_chunk_count(db, doc_id)
        assert count_before == 2

        # Delete document
        deleted_chunks = await delete_document_and_chunks(db, doc_id)
        assert deleted_chunks == 2

        # Verify document and chunks are gone
        docs = await get_all_documents(db)
        assert len(docs) == 0

    @pytest.mark.asyncio
    async def test_multiple_documents_independent(self, db):
        """Test that multiple documents don't interfere with each other."""
        doc_id1 = uuid4()
        doc_id2 = uuid4()

        doc1 = Document(
            id=doc_id1, filename="doc1.txt", description="Doc 1", uploaded_at="2026-05-25T00:00:00Z"
        )
        doc2 = Document(
            id=doc_id2, filename="doc2.txt", description="Doc 2", uploaded_at="2026-05-25T00:00:00Z"
        )
        db.add(doc1)
        db.add(doc2)
        await db.commit()

        # Add chunks to doc1
        chunk1 = DocumentChunk(
            id=uuid4(),
            source_type="document",
            source_id=doc_id1,
            content="Doc1 specific content",
            embedding=[0.1] * 1536,
        )
        db.add(chunk1)
        await db.commit()

        # Retrieve chunks for doc2 (should be empty)
        chunks2 = await get_document_chunks(db, doc_id2)
        assert len(chunks2) == 0

        # Retrieve chunks for doc1 (should have 1)
        chunks1 = await get_document_chunks(db, doc_id1)
        assert len(chunks1) == 1


class TestRAGFormatter:
    """Test formatting chunks for LLM context."""

    def test_format_chunks_empty(self):
        """Test formatting empty chunks."""
        result = format_chunks_for_context([])
        assert result == ""

    def test_format_chunks_single(self):
        """Test formatting a single chunk."""
        chunk = MagicMock()
        chunk.source_id = "doc-123"
        chunk.source_type = "document"
        chunk.content = "This is test content for the chunk"

        result = format_chunks_for_context([chunk])
        assert "Relevant Information" in result
        assert "test content" in result

    def test_format_chunks_multiple_same_source(self):
        """Test formatting multiple chunks from same source."""
        chunks = []
        for i in range(2):
            chunk = MagicMock()
            chunk.source_id = "doc-123"
            chunk.source_type = "document"
            chunk.content = f"Content chunk {i}"
            chunks.append(chunk)

        result = format_chunks_for_context(chunks)
        assert "Document 1" in result
        assert "Chunks 1-2" in result

    def test_format_chunks_multiple_sources(self):
        """Test formatting chunks from multiple sources."""
        chunk1 = MagicMock()
        chunk1.source_id = "doc-123"
        chunk1.source_type = "document"
        chunk1.content = "Content from doc 1"

        chunk2 = MagicMock()
        chunk2.source_id = "doc-456"
        chunk2.source_type = "document"
        chunk2.content = "Content from doc 2"

        result = format_chunks_for_context([chunk1, chunk2])
        assert "Document 1" in result
        assert "Document 2" in result
        assert "doc 1" in result
        assert "doc 2" in result

    def test_format_chunks_instruction_included(self):
        """Test that instruction for using chunks is included."""
        chunk = MagicMock()
        chunk.source_id = "doc-123"
        chunk.source_type = "document"
        chunk.content = "Test content"

        result = format_chunks_for_context([chunk])
        assert "Use this information" in result

    def test_format_citation_empty(self):
        """Test formatting citation for empty chunks."""
        result = format_chunks_for_citation([])
        assert result == ""

    def test_format_citation_single(self):
        """Test formatting citation for single chunk."""
        chunk = MagicMock()
        chunk.source_id = "doc-123"
        chunk.source_type = "document"

        result = format_chunks_for_citation([chunk])
        assert "Based on" in result
        assert "doc-123" in result

    def test_format_citation_multiple(self):
        """Test formatting citation for multiple chunks."""
        chunk1 = MagicMock()
        chunk1.source_id = "doc-123"
        chunk1.source_type = "document"

        chunk2 = MagicMock()
        chunk2.source_id = "doc-456"
        chunk2.source_type = "document"

        result = format_chunks_for_citation([chunk1, chunk2])
        assert "Based on" in result
        assert "doc-123" in result
        assert "doc-456" in result

    def test_format_citation_deduplicates_sources(self):
        """Test that citations deduplicate sources."""
        chunk1 = MagicMock()
        chunk1.source_id = "doc-123"
        chunk1.source_type = "document"

        chunk2 = MagicMock()
        chunk2.source_id = "doc-123"  # Same source
        chunk2.source_type = "document"

        result = format_chunks_for_citation([chunk1, chunk2])
        # Should only appear once
        assert result.count("doc-123") == 1


class TestRAGDocumentHandling:
    """Test document-specific RAG operations."""

    @pytest.mark.asyncio
    async def test_document_not_found_error(self, ):
        """Test error handling for nonexistent document."""
        # Use a mock database for this test
        mock_db = AsyncMock()

        with pytest.raises(ValueError):
            await delete_document_and_chunks(mock_db, uuid4())

    def test_chunk_content_preview(self):
        """Test that chunk content is properly previewed in formatting."""
        long_content = "A" * 200  # 200 characters
        chunk = MagicMock()
        chunk.source_id = "doc-123"
        chunk.source_type = "document"
        chunk.content = long_content

        result = format_chunks_for_context([chunk])
        # Preview should be truncated to 100 chars + "..."
        assert len(result) < 300  # Much less than full content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
