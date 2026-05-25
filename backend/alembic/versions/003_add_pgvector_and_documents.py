"""Add pgvector extension and document tables for v5 RAG system.

Revision ID: 003
Revises: 002
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Enable pgvector extension and create document storage tables for RAG.

    Tables:
    - documents: Metadata for uploaded files
    - document_chunks: Vector embeddings for semantic search (1536-dim OpenAI embeddings)
    """

    # Enable pgvector extension (idempotent - safe if already exists)
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create documents table for metadata
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_documents_uploaded_at', 'documents', ['uploaded_at'])

    # Create document_chunks table for vector embeddings
    # Stores chunks from documents, conversations, or facts - all co-located for RAG
    op.create_table(
        'document_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),  # 'conversation' | 'document' | 'fact'
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),  # references message, document, or fact id
        sa.Column('content', sa.Text(), nullable=False),  # Original chunk text
        sa.Column('embedding', Vector(1536), nullable=False),  # OpenAI text-embedding-3-small: 1536 dims
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for efficient retrieval
    op.create_index('ix_document_chunks_source', 'document_chunks', ['source_type', 'source_id'])
    op.create_index(
        'ix_document_chunks_embedding',
        'document_chunks',
        ['embedding'],
        postgresql_using='ivfflat',
        postgresql_ops={'embedding': 'vector_cosine_ops'}
    )


def downgrade() -> None:
    """
    Drop document tables and pgvector extension if rollback is needed.
    """
    # Drop indexes
    op.drop_index('ix_document_chunks_embedding', table_name='document_chunks')
    op.drop_index('ix_document_chunks_source', table_name='document_chunks')
    op.drop_index('ix_documents_uploaded_at', table_name='documents')

    # Drop tables
    op.drop_table('document_chunks')
    op.drop_table('documents')

    # pgvector extension left in place (safe, other systems might use it)
    # To fully remove: op.execute('DROP EXTENSION IF EXISTS vector')
