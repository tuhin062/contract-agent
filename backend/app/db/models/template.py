"""
Template database model for contract templates.
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base


class Template(Base):
    """Template model for reusable contract templates."""
    
    __tablename__ = "templates"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Template information
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    content = Column(Text, nullable=False)  # Template text with placeholders
    
    # Category/type
    category = Column(String)  # e.g., "NDA", "Service Agreement", "Purchase Order"
    
    # Template configuration
    placeholders = Column(JSONB, default=[])  # List of placeholder definitions
    # Example: [{"key": "{{COMPANY_NAME}}", "label": "Company Name", "type": "text"}]
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    custom_metadata = Column(JSONB, default={})

    
    # Ownership
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Template {self.name} ({self.category})>"
