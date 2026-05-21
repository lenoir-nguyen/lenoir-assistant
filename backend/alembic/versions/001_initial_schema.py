"""Create initial schema with pgvector extension and all tables.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    # pgvector extension is optional (for v5 RAG, skip for v4)
    # op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    # sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('is_owner', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('language', sa.String(10), server_default='en', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('modality', sa.String(10), server_default='text', nullable=False),
        sa.Column('language', sa.String(10), server_default='en', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_session_id', 'messages', ['session_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

    # Note: personal_facts, documents, and document_chunks tables are for v5 (RAG)
    # Commented out for v4 - will be added in a future migration when pgvector is available


def downgrade() -> None:
    # Note: RAG tables (personal_facts, documents, document_chunks) not present in v4

    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_session_id', table_name='messages')
    op.drop_table('messages')

    op.drop_table('sessions')

    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
