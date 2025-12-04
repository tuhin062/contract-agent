"""
Audit Log Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.db.models.audit import AuditAction


# Schema for audit log entry (response)
class AuditLogEntry(BaseModel):
    """Schema for audit log entry response."""
    id: UUID4
    user_id: UUID4
    action: AuditAction
    resource_type: str
    resource_id: Optional[UUID4] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schema for audit log list item (lighter version)
class AuditLogListItem(BaseModel):
    """Schema for audit log list item."""
    id: UUID4
    user_id: UUID4
    action: AuditAction
    resource_type: str
    resource_id: Optional[UUID4] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schema for filtering audit logs
class AuditLogFilters(BaseModel):
    """Schema for filtering audit logs."""
    user_id: Optional[UUID4] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID4] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)


# Schema for activity summary
class ActivitySummary(BaseModel):
    """Schema for activity summary."""
    total_actions: int
    actions_by_type: Dict[str, int] = {}
    period_start: datetime
    period_end: datetime

