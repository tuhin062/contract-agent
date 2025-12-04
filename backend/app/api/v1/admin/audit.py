"""
Admin audit log endpoints for compliance and monitoring.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.db.crud.audit import (
    get_audit_logs,
    get_audit_log,
    get_audit_logs_count,
    get_resource_history,
    get_user_activity,
    get_failed_logins,
    get_security_events
)
from app.db.models.user import User
from app.db.models.audit import AuditAction, AuditLog
from app.api.deps import require_admin
from app.core.errors import NotFoundException

router = APIRouter()


class AuditLogResponse(BaseModel):
    """Audit log response schema."""
    model_config = {"from_attributes": True}
    
    id: UUID
    action: AuditAction
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    description: str
    details: dict = {}
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    success: str
    error_message: Optional[str] = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response."""
    items: List[AuditLogResponse]
    total: int
    skip: int
    limit: int


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    user_id: Optional[UUID] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    success: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List audit logs with filters (admin only).
    
    Supports filtering by:
    - user_id: Filter by user who performed action
    - action: Filter by action type
    - resource_type: Filter by resource type (user, contract, template, etc.)
    - resource_id: Filter by specific resource
    - start_date/end_date: Date range filter
    - success: Filter by status (success, failure, error)
    """
    logs = get_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        success=success
    )
    
    total = get_audit_logs_count(
        db=db,
        user_id=user_id,
        action=action,
        start_date=start_date,
        end_date=end_date
    )
    
    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/stats")
async def get_audit_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get audit log statistics for the specified number of days."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total = get_audit_logs_count(db, start_date=start_date)
    logins = get_audit_logs_count(db, action=AuditAction.LOGIN, start_date=start_date)
    failed_logins = get_audit_logs_count(db, action=AuditAction.LOGIN_FAILED, start_date=start_date)
    
    # Get counts by action type
    action_counts = {}
    for action in AuditAction:
        count = get_audit_logs_count(db, action=action, start_date=start_date)
        if count > 0:
            action_counts[action.value] = count
    
    return {
        "period_days": days,
        "total_events": total,
        "logins": logins,
        "failed_logins": failed_logins,
        "by_action": action_counts
    }


@router.get("/security")
async def get_security_audit(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get security-related audit events."""
    events = get_security_events(db, hours=hours)
    failed = get_failed_logins(db, hours=hours)
    
    return {
        "period_hours": hours,
        "security_events": [AuditLogResponse.model_validate(e) for e in events],
        "failed_logins": [AuditLogResponse.model_validate(f) for f in failed],
        "failed_login_count": len(failed)
    }


@router.get("/resource/{resource_type}/{resource_id}")
async def get_resource_audit_history(
    resource_type: str,
    resource_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get audit history for a specific resource."""
    history = get_resource_history(db, resource_type, resource_id, limit)
    
    return {
        "resource_type": resource_type,
        "resource_id": str(resource_id),
        "history": [AuditLogResponse.model_validate(h) for h in history]
    }


@router.get("/user/{user_id}/activity")
async def get_user_activity_log(
    user_id: UUID,
    days: int = Query(30, ge=1, le=90),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get activity log for a specific user."""
    activity = get_user_activity(db, user_id, days, limit)
    
    return {
        "user_id": str(user_id),
        "period_days": days,
        "activity": [AuditLogResponse.model_validate(a) for a in activity]
    }


@router.get("/{audit_id}", response_model=AuditLogResponse)
async def get_audit_log_detail(
    audit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get audit log details by ID."""
    log = get_audit_log(db, audit_id)
    if not log:
        raise NotFoundException(detail="Audit log not found")
    
    return AuditLogResponse.model_validate(log)

