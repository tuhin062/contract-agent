"""Add conversations and AI interaction logs tables

Revision ID: add_conversations_002
Revises: add_audit_logs_001
Create Date: 2025-12-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'add_conversations_002'
down_revision: Union[str, None] = 'add_audit_logs_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.Enum('active', 'archived', 'deleted', name='conversationstatus'), nullable=False),
        sa.Column('context_file_ids', postgresql.ARRAY(sa.UUID()), nullable=True, server_default='{}'),
        sa.Column('total_messages', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tokens_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # Create conversation_messages table
    op.create_table('conversation_messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('confidence', sa.String(20), nullable=True),
        sa.Column('retrieved_chunks', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('follow_up_suggestions', postgresql.ARRAY(sa.String()), nullable=True, server_default='{}'),
        sa.Column('extracted_clauses', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('risk_highlights', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('tokens_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_messages_id'), 'conversation_messages', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_messages_conversation_id'), 'conversation_messages', ['conversation_id'], unique=False)

    # Create ai_interaction_logs table
    op.create_table('ai_interaction_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=True),
        sa.Column('interaction_type', sa.String(50), nullable=False),
        sa.Column('model_used', sa.String(100), nullable=False),
        sa.Column('input_summary', sa.Text(), nullable=True),
        sa.Column('output_summary', sa.Text(), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('output_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('context_file_ids', postgresql.ARRAY(sa.UUID()), nullable=True, server_default='{}'),
        sa.Column('retrieved_chunk_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('confidence_level', sa.String(20), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_interaction_logs_id'), 'ai_interaction_logs', ['id'], unique=False)
    op.create_index(op.f('ix_ai_interaction_logs_user_id'), 'ai_interaction_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_interaction_logs_user_id'), table_name='ai_interaction_logs')
    op.drop_index(op.f('ix_ai_interaction_logs_id'), table_name='ai_interaction_logs')
    op.drop_table('ai_interaction_logs')
    
    op.drop_index(op.f('ix_conversation_messages_conversation_id'), table_name='conversation_messages')
    op.drop_index(op.f('ix_conversation_messages_id'), table_name='conversation_messages')
    op.drop_table('conversation_messages')
    
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    op.drop_table('conversations')
    
    op.execute('DROP TYPE IF EXISTS conversationstatus')
    op.execute('DROP TYPE IF EXISTS messagerole')



