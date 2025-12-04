"""
Template Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any, List
from datetime import datetime


# Placeholder definition schema
class TemplatePlaceholder(BaseModel):
    """Schema for template placeholder definition."""
    key: str = Field(..., description="Placeholder key, e.g., {{COMPANY_NAME}}")
    label: str = Field(..., description="Human-readable label")
    type: str = Field("text", description="Input type: text, number, date, etc.")
    required: bool = Field(True, description="Whether this field is required")
    default: Optional[str] = Field(None, description="Default value")


# Base schema
class TemplateBase(BaseModel):
    """Base template schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    category: Optional[str] = None


# Schema for creating a template
class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    placeholders: List[TemplatePlaceholder] = []
    metadata: Dict[str, Any] = {}


# Schema for updating a template
class TemplateUpdate(BaseModel):
    """Schema for updating template information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    placeholders: Optional[List[TemplatePlaceholder]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


# Schema for template in database (response)
class Template(TemplateBase):
    """Schema for template response."""
    id: UUID4
    placeholders: List[Dict[str, Any]] = []
    is_active: bool
    metadata: Dict[str, Any] = {}
    created_by: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schema for template list item
class TemplateListItem(BaseModel):
    """Schema for template list item."""
    id: UUID4
    name: str
    category: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schema for generating contract from template
class GenerateFromTemplate(BaseModel):
    """Schema for generating a contract from template."""
    template_id: UUID4
    title: str = Field(..., min_length=1, max_length=500)
    values: Dict[str, str] = Field(..., description="Placeholder values")
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
