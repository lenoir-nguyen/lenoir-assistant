"""Add personal_facts table for v4.1 short-term memory feature.

Revision ID: 002
Revises: 001
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create personal_facts table for storing long-term facts (owners only)."""
    op.create_table(
        'personal_facts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for fast retrieval
    op.create_index('ix_personal_facts_category', 'personal_facts', ['category'])
    op.create_index('ix_personal_facts_created_at', 'personal_facts', ['created_at'], postgresql_using='btree')


def downgrade() -> None:
    """Drop personal_facts table if rollback is needed."""
    op.drop_index('ix_personal_facts_created_at', table_name='personal_facts')
    op.drop_index('ix_personal_facts_category', table_name='personal_facts')
    op.drop_table('personal_facts')
