"""
Upload Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime
from app.db.models.upload import FileType, ExtractionStatus


# Base schema
class UploadBase(BaseModel):
    """Base upload schema."""
    filename: str
    file_type: FileType
    size: int = Field(..., gt=0, description="File size in bytes")
    mime_type: Optional[str] = None


# Schema for upload response
class Upload(UploadBase):
    """Schema for upload response."""
    id: UUID4
    path: str
    text_extraction_status: ExtractionStatus
    pages_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="custom_metadata")
    uploaded_by: UUID4
    uploaded_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both alias and field name


# Schema for upload list item (lighter version)
class UploadListItem(BaseModel):
    """Schema for upload list item."""
    id: UUID4
    filename: str
    file_type: FileType
    size: int
    text_extraction_status: ExtractionStatus
    uploaded_by: UUID4
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Schema for extracted text response
class ExtractedText(BaseModel):
    """Schema for extracted text response."""
    file_id: UUID4
    status: ExtractionStatus
    pages_count: Optional[int] = None
    text: Optional[str] = None  # Full text if completed
    chunks: Optional[list] = None  # Text chunks if available
    error: Optional[str] = None  # Error message if failed


# Schema for upload filters
class UploadFilters(BaseModel):
    """Schema for filtering uploads."""
    file_type: Optional[FileType] = None
    status: Optional[ExtractionStatus] = None
    uploaded_by: Optional[UUID4] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)
