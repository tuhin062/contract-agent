"""
Contract database model with versioning and approval workflow.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.session import Base


class ContractStatus(str, enum.Enum):
    """Contract status enumeration."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    ARCHIVED = "archived"


class Contract(Base):
    """Contract model with versioning and approval workflow."""
    
    __tablename__ = "contracts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Contract information
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)  # Full contract text
    
    # Status and workflow
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT, nullable=False)
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    parent_contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True)
    is_latest_version = Column(Boolean, default=True, nullable=False)
    
    # Template reference (if created from template)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=True)
    
    # Metadata
    custom_metadata = Column(JSONB, default={})  # Custom fields, tags, etc.
    
    # Ownership and review
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Review feedback
    review_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    executed_at = Column(DateTime(timezone=True))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    template = relationship("Template", foreign_keys=[template_id])
    parent = relationship("Contract", remote_side=[id], foreign_keys=[parent_contract_id])
    
    def __repr__(self):
        return f"<Contract {self.title} v{self.version} ({self.status})>"
