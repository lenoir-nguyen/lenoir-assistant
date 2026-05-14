from sqlalchemy import Column, String, Text, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()


class Session(Base):
    """User session — tracks whether this is the owner or a stranger."""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_owner = Column(Boolean, default=False, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session {self.id} owner={self.is_owner} lang={self.language}>"


class Message(Base):
    """Chat message — stores both text and voice modality."""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    modality = Column(String(10), default="text", nullable=False)  # 'text' | 'voice'
    language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("Session", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_session_id", "session_id"),
        Index("ix_messages_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Message {self.id} role={self.role} modality={self.modality}>"


class PersonalFact(Base):
    """Structured personal knowledge about Lenoir."""
    __tablename__ = "personal_facts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(100), nullable=False)  # e.g. 'preference', 'contact', 'event'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_personal_facts_category", "category"),
    )

    def __repr__(self):
        return f"<PersonalFact {self.id} category={self.category}>"


class Document(Base):
    """Metadata for uploaded documents."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    description = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_documents_uploaded_at", "uploaded_at"),
    )

    def __repr__(self):
        return f"<Document {self.id} filename={self.filename}>"


class DocumentChunk(Base):
    """Vector embeddings for RAG retrieval — from messages, documents, or facts."""
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(50), nullable=False)  # 'conversation' | 'document' | 'fact'
    source_id = Column(UUID(as_uuid=True), nullable=False)  # references message, document, or fact id
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)  # OpenAI text-embedding-3-small
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_document_chunks_source", "source_type", "source_id"),
        Index("ix_document_chunks_embedding", "embedding", postgresql_using="ivfflat"),
    )

    def __repr__(self):
        return f"<DocumentChunk {self.id} source={self.source_type}>"
