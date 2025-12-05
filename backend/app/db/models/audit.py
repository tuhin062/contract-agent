"""
Audit Log database model for tracking user actions and system events.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ENUM
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.session import Base




class AuditAction(str, enum.Enum):
    """Audit action types."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    
    # User Management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"
    USER_ACTIVATED = "user_activated"
    USER_DELETED = "user_deleted"
    
    # Contracts
    CONTRACT_CREATED = "contract_created"
    CONTRACT_UPDATED = "contract_updated"
    CONTRACT_SUBMITTED = "contract_submitted"
    CONTRACT_APPROVED = "contract_approved"
    CONTRACT_REJECTED = "contract_rejected"
    CONTRACT_EXECUTED = "contract_executed"
    CONTRACT_ARCHIVED = "contract_archived"
    CONTRACT_VERSIONED = "contract_versioned"
    
    # Templates
    TEMPLATE_CREATED = "template_created"
    TEMPLATE_UPDATED = "template_updated"
    TEMPLATE_DELETED = "template_deleted"
    
    # Uploads
    FILE_UPLOADED = "file_uploaded"
    FILE_DELETED = "file_deleted"
    FILE_INDEXED = "file_indexed"
    
    # Proposals/Validation
    PROPOSAL_CREATED = "proposal_created"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    VALIDATION_FAILED = "validation_failed"
    
    # Chat/RAG
    CHAT_MESSAGE = "chat_message"
    
    # Admin
    SETTINGS_UPDATED = "settings_updated"
    
    # System
    SYSTEM_ERROR = "system_error"


class AuditLog(Base):
    """Audit log for tracking all user and system actions."""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Action information
    # Use PostgreSQL ENUM - we'll ensure values are converted correctly in CRUD
    action = Column(ENUM(AuditAction, name='auditaction', create_type=False, values_callable=lambda obj: [e.value for e in obj]), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)  # e.g., "contract", "user", "template"
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # ID of affected resource
    
    # Description and details
    description = Column(Text, nullable=False)
    details = Column(JSONB, default={})  # Additional context (old values, new values, etc.)
    
    # User who performed the action (null for system actions)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Request context
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True)  # For tracing
    
    # Status
    success = Column(String(10), default="success")  # success, failure, error
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<AuditLog {self.action} by user {self.user_id} at {self.created_at}>"
