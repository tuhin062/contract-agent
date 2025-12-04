"""
Admin endpoints for user management, settings, and system administration.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, Field

from app.db.session import get_db
from app.db.crud.user import (
    get_users,
    get_user,
    get_user_by_email,
    create_user,
    update_user,
    update_password,
    deactivate_user,
    activate_user,
    change_user_role,
    get_users_count
)
from app.db.crud.contract import get_contracts
from app.db.crud.audit import get_audit_logs, get_audit_logs_count
from app.db.models.user import User, UserRole
from app.db.models.audit import AuditAction
from app.db.crud.audit import create_audit_log
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.schemas.audit import AuditLogEntry, AuditLogListItem
from app.schemas.contract import ContractFilters
from app.api.deps import get_current_user, require_admin
from app.core.errors import NotFoundException, ConflictException, ForbiddenException

router = APIRouter()


# ============ User Management ============

@router.get("/users", response_model=List[UserSchema])
async def list_users(
    role: UserRole = None,
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all users (admin only)."""
    users = get_users(db, skip=skip, limit=limit, role=role, is_active=is_active)
    return [UserSchema.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_details(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get user details by ID (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    return UserSchema.model_validate(user)


@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (admin only)."""
    # Check if email already exists
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise ConflictException(detail="Email already registered")
    
    user = create_user(db, user_in)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.USER_CREATED,
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email, "role": user.role.value},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return UserSchema.model_validate(user)


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user_details(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user details (admin only)."""
    # Check if user exists
    existing = get_user(db, user_id)
    if not existing:
        raise NotFoundException(detail="User not found")
    
    # If email is being changed, check for conflicts
    if user_update.email and user_update.email != existing.email:
        email_conflict = get_user_by_email(db, user_update.email)
        if email_conflict:
            raise ConflictException(detail="Email already in use")
    
    user = update_user(db, user_id, user_update)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.USER_UPDATED,
        resource_type="user",
        resource_id=existing.id,
        details={"changes": user_update.model_dump(exclude_unset=True)},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return UserSchema.model_validate(user)


class PasswordChange(BaseModel):
    """Schema for password change."""
    new_password: str = Field(..., min_length=8, max_length=100)


@router.post("/users/{user_id}/password")
async def change_user_password(
    user_id: str,
    password_data: PasswordChange,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Change user password (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    
    update_password(db, user_id, password_data.new_password)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.PASSWORD_CHANGED,
        resource_type="user",
        resource_id=user.id,
        details={"changed_by_admin": True},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Password updated successfully"}


@router.post("/users/{user_id}/deactivate", response_model=UserSchema)
async def deactivate_user_account(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Deactivate a user account (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    
    # Can't deactivate yourself
    if str(user.id) == str(current_user.id):
        raise ForbiddenException(detail="Cannot deactivate your own account")
    
    updated_user = deactivate_user(db, user_id)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.USER_DEACTIVATED,
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return UserSchema.model_validate(updated_user)


@router.post("/users/{user_id}/activate", response_model=UserSchema)
async def activate_user_account(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Activate a user account (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    
    updated_user = activate_user(db, user_id)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.USER_ACTIVATED,
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return UserSchema.model_validate(updated_user)


class RoleChange(BaseModel):
    """Schema for role change."""
    role: UserRole


@router.post("/users/{user_id}/role", response_model=UserSchema)
async def change_role(
    user_id: str,
    role_data: RoleChange,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Change user role (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    
    old_role = user.role
    updated_user = change_user_role(db, user_id, role_data.role)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.USER_ROLE_CHANGED,
        resource_type="user",
        resource_id=user.id,
        details={"old_role": old_role.value, "new_role": role_data.role.value},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return UserSchema.model_validate(updated_user)


# ============ Audit Logs ============

@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def list_audit_logs(
    user_id: str = None,
    action: AuditAction = None,
    resource_type: str = None,
    resource_id: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List audit logs (admin only)."""
    logs = get_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return [AuditLogEntry.model_validate(log) for log in logs]


# ============ System Statistics ============

class SystemStats(BaseModel):
    """System statistics response."""
    total_users: int
    active_users: int
    total_contracts: int
    pending_contracts: int
    total_audit_logs: int
    users_by_role: dict
    contracts_by_status: dict


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get system statistics (admin only)."""
    from app.db.models.contract import Contract, ContractStatus
    
    # User counts
    total_users = get_users_count(db)
    active_users = get_users_count(db, is_active=True)
    
    # Users by role
    users_by_role = {}
    for role in UserRole:
        users_by_role[role.value] = get_users_count(db, role=role)
    
    # Contract counts
    total_contracts = db.query(Contract).count()
    pending_contracts = db.query(Contract).filter(
        Contract.status == ContractStatus.PENDING_REVIEW
    ).count()
    
    # Contracts by status
    contracts_by_status = {}
    for status in ContractStatus:
        contracts_by_status[status.value] = db.query(Contract).filter(
            Contract.status == status
        ).count()
    
    # Audit logs count
    total_audit_logs = get_audit_logs_count(db)
    
    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_contracts=total_contracts,
        pending_contracts=pending_contracts,
        total_audit_logs=total_audit_logs,
        users_by_role=users_by_role,
        contracts_by_status=contracts_by_status
    )


# ============ Model Configuration ============

class ModelConfig(BaseModel):
    """LLM model configuration."""
    chat_model: str
    reasoning_model: str
    generation_model: str
    embedding_model: str


@router.get("/settings/models", response_model=ModelConfig)
async def get_model_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get current LLM model configuration (admin only)."""
    from app.core.config import settings
    
    return ModelConfig(
        chat_model=settings.OPENROUTER_CHAT_MODEL,
        reasoning_model=settings.OPENROUTER_REASONING_MODEL,
        generation_model=settings.OPENROUTER_GENERATION_MODEL,
        embedding_model=settings.OPENROUTER_EMBEDDING_MODEL
    )

