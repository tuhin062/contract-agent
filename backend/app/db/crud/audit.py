"""
CRUD operations for Audit Log model.
Handles audit log creation and retrieval for compliance tracking.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta

from app.db.models.audit import AuditLog, AuditAction


def create_audit_log(
    db: Session,
    action: AuditAction,
    description: str,
    user_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    details: dict = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
    success: str = "success",
    error_message: Optional[str] = None
) -> AuditLog:
    """
    Create a new audit log entry.
    
    Args:
        db: Database session
        action: Type of action performed
        description: Human-readable description
        user_id: ID of user who performed action (None for system)
        resource_type: Type of resource affected
        resource_id: ID of resource affected
        details: Additional context as JSON
        ip_address: Client IP address
        user_agent: Client user agent
        request_id: Request ID for tracing
        success: Status (success, failure, error)
        error_message: Error message if failed
        
    Returns:
        Created audit log entry
    """
    audit_log = AuditLog(
        action=action,
        description=description,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        success=success,
        error_message=error_message
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    success: Optional[str] = None
) -> List[AuditLog]:
    """
    Get audit logs with optional filters.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        user_id: Filter by user
        action: Filter by action type
        resource_type: Filter by resource type
        resource_id: Filter by specific resource
        start_date: Filter by start date
        end_date: Filter by end date
        success: Filter by success status
    """
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if resource_id:
        query = query.filter(AuditLog.resource_id == resource_id)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    if success:
        query = query.filter(AuditLog.success == success)
    
    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


def get_audit_log(db: Session, audit_id: UUID) -> Optional[AuditLog]:
    """Get single audit log by ID."""
    return db.query(AuditLog).filter(AuditLog.id == audit_id).first()


def get_audit_logs_count(
    db: Session,
    user_id: Optional[UUID] = None,
    action: Optional[AuditAction] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> int:
    """Get count of audit logs with optional filters."""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    return query.count()


def get_resource_history(
    db: Session,
    resource_type: str,
    resource_id: UUID,
    limit: int = 50
) -> List[AuditLog]:
    """Get audit history for a specific resource."""
    return db.query(AuditLog).filter(
        AuditLog.resource_type == resource_type,
        AuditLog.resource_id == resource_id
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()


def get_user_activity(
    db: Session,
    user_id: UUID,
    days: int = 30,
    limit: int = 100
) -> List[AuditLog]:
    """Get recent activity for a specific user."""
    start_date = datetime.utcnow() - timedelta(days=days)
    return db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.created_at >= start_date
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()


def get_failed_logins(
    db: Session,
    hours: int = 24,
    limit: int = 100
) -> List[AuditLog]:
    """Get recent failed login attempts."""
    start_date = datetime.utcnow() - timedelta(hours=hours)
    return db.query(AuditLog).filter(
        AuditLog.action == AuditAction.LOGIN_FAILED,
        AuditLog.created_at >= start_date
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()


def get_security_events(
    db: Session,
    hours: int = 24,
    limit: int = 100
) -> List[AuditLog]:
    """Get security-related events."""
    start_date = datetime.utcnow() - timedelta(hours=hours)
    security_actions = [
        AuditAction.LOGIN,
        AuditAction.LOGOUT,
        AuditAction.LOGIN_FAILED,
        AuditAction.PASSWORD_CHANGED,
        AuditAction.USER_DEACTIVATED,
        AuditAction.USER_DELETED
    ]
    return db.query(AuditLog).filter(
        AuditLog.action.in_(security_actions),
        AuditLog.created_at >= start_date
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()


def cleanup_old_logs(db: Session, days: int = 365) -> int:
    """
    Delete audit logs older than specified days.
    Returns count of deleted records.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    result = db.query(AuditLog).filter(
        AuditLog.created_at < cutoff_date
    ).delete(synchronize_session=False)
    db.commit()
    return result
