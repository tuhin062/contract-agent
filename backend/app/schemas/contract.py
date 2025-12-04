"""
Contract Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime
from app.db.models.contract import ContractStatus


# Base schema
class ContractBase(BaseModel):
    """Base contract schema."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)


# Schema for creating a contract
class ContractCreate(ContractBase):
    """Schema for creating a new contract."""
    template_id: Optional[UUID4] = None
    metadata: Dict[str, Any] = {}


# Schema for updating a contract
class ContractUpdate(BaseModel):
    """Schema for updating contract information."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


# Schema for contract in database (response)
class Contract(ContractBase):
    """Schema for contract response."""
    id: UUID4
    status: ContractStatus
    version: int
    is_latest_version: bool
    parent_contract_id: Optional[UUID4] = None
    template_id: Optional[UUID4] = None
    metadata: Dict[str, Any] = {}
    created_by: UUID4
    reviewed_by: Optional[UUID4] = None
    approved_by: Optional[UUID4] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schema for contract list item (lighter version)
class ContractListItem(BaseModel):
    """Schema for contract list item."""
    id: UUID4
    title: str
    status: ContractStatus
    version: int
    is_latest_version: bool
    created_by: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schema for contract approval/rejection
class ContractReview(BaseModel):
    """Schema for reviewing a contract."""
    notes: Optional[str] = Field(None, max_length=2000)


class ContractRejection(BaseModel):
    """Schema for rejecting a contract."""
    reason: str = Field(..., min_length=1, max_length=2000)


# Schema for filtering contracts
class ContractFilters(BaseModel):
    """Schema for filtering contracts."""
    status: Optional[ContractStatus] = None
    created_by: Optional[UUID4] = None
    template_id: Optional[UUID4] = None
    latest_only: bool = True
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)
