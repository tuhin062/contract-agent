"""
Upload/File database model for tracking uploaded documents.
"""
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.session import Base


class FileType(str, enum.Enum):
    """File type enumeration."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    OTHER = "other"


class ExtractionStatus(str, enum.Enum):
    """Text extraction status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Upload(Base):
    """Upload model for tracking uploaded files and their metadata."""
    
    __tablename__ = "uploads"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # File information
    filename = Column(String, nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    path = Column(String, nullable=False, unique=True)  # Storage path
    size = Column(Integer, nullable=False)  # File size in bytes
    mime_type = Column(String)
    
    # Text extraction
    text_extraction_status = Column(
        Enum(ExtractionStatus),
        default=ExtractionStatus.PENDING,
        nullable=False
    )
    pages_count = Column(Integer)  # Number of pages (for PDFs)
    extracted_text_path = Column(String)  # Path to extracted text JSON
    
    # Metadata
    custom_metadata = Column(JSONB, default={})  # Additional file-specific metadata
    
    # Ownership
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f"<Upload {self.filename} ({self.file_type})>"
