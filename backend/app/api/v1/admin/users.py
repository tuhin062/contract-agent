"""
Admin user management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.db.crud.user import (
    get_user,
    get_users,
    get_users_count,
    create_user,
    update_user,
    update_password,
    deactivate_user,
    activate_user,
    delete_user,
    search_users
)
from app.db.crud.audit import create_audit_log
from app.db.models.user import User, UserRole
from app.db.models.audit import AuditAction
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.api.deps import get_current_user, require_admin
from app.core.errors import NotFoundException, ConflictException, BadRequestException

router = APIRouter()


class UserListResponse:
    """Response for user list with pagination."""
    pass


@router.get("", response_model=List[UserSchema])
async def list_users(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all users (admin only).
    
    Supports filtering by role, active status, and search by name/email.
    """
    if search:
        users = search_users(db, search, skip, limit)
    else:
        users = get_users(db, skip, limit, role, is_active)
    
    return [UserSchema.model_validate(u) for u in users]


@router.get("/stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get user statistics."""
    return {
        "total": get_users_count(db),
        "active": get_users_count(db, is_active=True),
        "inactive": get_users_count(db, is_active=False),
        "by_role": {
            "admin": get_users_count(db, role=UserRole.ADMIN),
            "reviewer": get_users_count(db, role=UserRole.REVIEWER),
            "regular": get_users_count(db, role=UserRole.REGULAR)
        }
    }


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (admin only)."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from app.db.crud.user import get_user_by_email
        
        logger.info(f"Creating user: email={user_data.email}, role={user_data.role}")
        
        # Check if email already exists
        existing = get_user_by_email(db, user_data.email)
        if existing:
            logger.warning(f"User creation failed: email {user_data.email} already exists")
            raise ConflictException(detail="Email already registered")
        
        # Create user
        try:
            new_user = create_user(db, user_data)
            logger.info(f"User created successfully: id={new_user.id}, email={new_user.email}")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
        
        # Audit log
        try:
            create_audit_log(
                db=db,
                action=AuditAction.USER_CREATED,
                description=f"User '{new_user.email}' created by admin",
                user_id=current_user.id,
                resource_type="user",
                resource_id=new_user.id,
                details={"email": new_user.email, "role": new_user.role.value}
            )
        except Exception as e:
            # Log audit failure but don't fail the request
            logger.warning(f"Failed to create audit log: {str(e)}")
        
        return UserSchema.model_validate(new_user)
    except (ConflictException, HTTPException):
        # Re-raise known exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_new_user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_details(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get user details by ID (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    return UserSchema.model_validate(user)


@router.put("/{user_id}", response_model=UserSchema)
async def update_user_details(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user details (admin only)."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Prevent self-demotion
        if user_id == current_user.id and user_update.role and user_update.role != UserRole.ADMIN:
            raise BadRequestException(detail="Cannot demote yourself from admin role")
        
        updated = update_user(db, user_id, user_update)
        if not updated:
            raise NotFoundException(detail="User not found")
        
        # Serialize user BEFORE attempting audit log
        try:
            user_schema = UserSchema.model_validate(updated)
        except Exception as e:
            logger.error(f"Error serializing user: {str(e)}", exc_info=True)
            db.rollback()
            db.refresh(updated)
            user_schema = UserSchema.model_validate(updated)
        
        # Audit log (non-blocking - don't fail if it errors)
        try:
            create_audit_log(
                db=db,
                action=AuditAction.USER_UPDATED,
                description=f"User '{updated.email}' updated by admin",
                user_id=current_user.id,
                resource_type="user",
                resource_id=user_id,
                details=user_update.model_dump(exclude_unset=True)
            )
        except Exception as e:
            # Log audit failure but don't fail the request
            logger.warning(f"Failed to create audit log (non-critical): {str(e)}")
            # Rollback any partial audit log transaction
            try:
                db.rollback()
            except Exception:
                pass
        
        return user_schema
        
    except (BadRequestException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_user_details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    new_password: str = Field(..., min_length=8, max_length=100)


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: UUID,
    password_data: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Reset a user's password (admin only)."""
    updated = update_password(db, user_id, password_data.new_password)
    if not updated:
        raise NotFoundException(detail="User not found")
    
    # Audit log
    create_audit_log(
        db=db,
        action=AuditAction.PASSWORD_CHANGED,
        description=f"Password reset by admin for user '{updated.email}'",
        user_id=current_user.id,
        resource_type="user",
        resource_id=user_id
    )
    
    return {"message": "Password reset successfully"}


@router.post("/{user_id}/deactivate", response_model=UserSchema)
async def deactivate_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Deactivate a user (admin only)."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Prevent self-deactivation
        if user_id == current_user.id:
            raise BadRequestException(detail="Cannot deactivate yourself")
        
        deactivated = deactivate_user(db, user_id)
        if not deactivated:
            raise NotFoundException(detail="User not found")
        
        # Serialize user BEFORE attempting audit log
        try:
            user_schema = UserSchema.model_validate(deactivated)
        except Exception as e:
            logger.error(f"Error serializing user: {str(e)}", exc_info=True)
            db.rollback()
            db.refresh(deactivated)
            user_schema = UserSchema.model_validate(deactivated)
        
        # Audit log (non-blocking - don't fail if it errors)
        try:
            create_audit_log(
                db=db,
                action=AuditAction.USER_DEACTIVATED,
                description=f"User '{deactivated.email}' deactivated by admin",
                user_id=current_user.id,
                resource_type="user",
                resource_id=user_id
            )
        except Exception as e:
            # Log audit failure but don't fail the request
            logger.warning(f"Failed to create audit log (non-critical): {str(e)}")
            # Rollback any partial audit log transaction
            try:
                db.rollback()
            except Exception:
                pass
        
        return user_schema
        
    except (BadRequestException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in deactivate_user_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/{user_id}/activate", response_model=UserSchema)
async def activate_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Activate a user (admin only)."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        activated = activate_user(db, user_id)
        if not activated:
            raise NotFoundException(detail="User not found")
        
        # Serialize user BEFORE attempting audit log
        try:
            user_schema = UserSchema.model_validate(activated)
        except Exception as e:
            logger.error(f"Error serializing user: {str(e)}", exc_info=True)
            db.rollback()
            db.refresh(activated)
            user_schema = UserSchema.model_validate(activated)
        
        # Audit log (non-blocking - don't fail if it errors)
        try:
            create_audit_log(
                db=db,
                action=AuditAction.USER_ACTIVATED,
                description=f"User '{activated.email}' activated by admin",
                user_id=current_user.id,
                resource_type="user",
                resource_id=user_id
            )
        except Exception as e:
            # Log audit failure but don't fail the request
            logger.warning(f"Failed to create audit log (non-critical): {str(e)}")
            # Rollback any partial audit log transaction
            try:
                db.rollback()
            except Exception:
                pass
        
        return user_schema
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in activate_user_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user permanently (admin only). Use with caution."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Prevent self-deletion
        if user_id == current_user.id:
            raise BadRequestException(detail="Cannot delete yourself")
        
        # Get user info before deletion (for audit log)
        user = get_user(db, user_id)
        if not user:
            raise NotFoundException(detail="User not found")
        
        # Capture user info before deletion
        user_email = user.email
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        logger.info(f"Deleting user: id={user_id}, email={user_email}")
        
        # Delete the user
        try:
            deleted = delete_user(db, user_id)
            if not deleted:
                raise NotFoundException(detail="User not found")
            logger.info(f"User deleted successfully: id={user_id}, email={user_email}")
        except Exception as e:
            db.rollback()  # Ensure session is clean
            error_msg = str(e)
            
            # Check for foreign key constraint violations
            if "foreign key" in error_msg.lower() or "violates foreign key" in error_msg.lower():
                logger.warning(f"Cannot delete user {user_id}: User has related records (contracts, uploads, etc.)")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete user: User has related records (contracts, uploads, proposals, etc.). Please deactivate the user instead or remove related records first."
                )
            
            logger.error(f"Error deleting user: {error_msg}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete user: {error_msg}"
            )
        
        # Audit log (non-blocking - don't fail if it errors)
        try:
            create_audit_log(
                db=db,
                action=AuditAction.USER_DELETED,
                description=f"User '{user_email}' permanently deleted by admin",
                user_id=current_user.id,
                resource_type="user",
                resource_id=user_id,
                details={"email": user_email, "role": user_role}
            )
        except Exception as e:
            # Log audit failure but don't fail the request
            logger.warning(f"Failed to create audit log (non-critical): {str(e)}")
            # Rollback any partial audit log transaction
            try:
                db.rollback()
            except Exception:
                pass
        
        return None
        
    except (BadRequestException, NotFoundException, HTTPException):
        # Re-raise known exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_user_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

