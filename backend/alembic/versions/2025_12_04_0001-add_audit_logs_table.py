"""Add audit logs table

Revision ID: add_audit_logs_001
Revises: 311a6839b999
Create Date: 2025-12-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_audit_logs_001'
down_revision: Union[str, None] = '311a6839b999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create audit action enum
    audit_action_enum = postgresql.ENUM(
        'login', 'logout', 'login_failed', 'password_changed',
        'user_created', 'user_updated', 'user_deactivated', 'user_activated', 'user_deleted',
        'contract_created', 'contract_updated', 'contract_submitted', 'contract_approved',
        'contract_rejected', 'contract_executed', 'contract_archived', 'contract_versioned',
        'template_created', 'template_updated', 'template_deleted',
        'file_uploaded', 'file_deleted', 'file_indexed',
        'proposal_created', 'validation_started', 'validation_completed', 'validation_failed',
        'chat_message', 'settings_updated', 'system_error',
        name='auditaction',
        create_type=True
    )
    audit_action_enum.create(op.get_bind(), checkfirst=True)
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('action', sa.Enum(
            'login', 'logout', 'login_failed', 'password_changed',
            'user_created', 'user_updated', 'user_deactivated', 'user_activated', 'user_deleted',
            'contract_created', 'contract_updated', 'contract_submitted', 'contract_approved',
            'contract_rejected', 'contract_executed', 'contract_archived', 'contract_versioned',
            'template_created', 'template_updated', 'template_deleted',
            'file_uploaded', 'file_deleted', 'file_indexed',
            'proposal_created', 'validation_started', 'validation_completed', 'validation_failed',
            'chat_message', 'settings_updated', 'system_error',
            name='auditaction'
        ), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.UUID(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('success', sa.String(length=10), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_id'), 'audit_logs', ['resource_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_resource_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    
    # Drop enum
    sa.Enum(name='auditaction').drop(op.get_bind(), checkfirst=True)

