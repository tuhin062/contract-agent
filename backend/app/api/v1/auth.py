"""
Authentication endpoints for login, logout, and token refresh.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.db.crud.user import get_user_by_email, update_last_login, create_user, update_password
from app.schemas.user import UserLogin, Token, TokenRefresh, User, UserCreate
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.errors import UnauthorizedException, NotFoundException, BadRequestException
from app.api.deps import get_current_user, require_admin

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)  # Only admin can create users
):
    """
    Register a new user (admin only).
    
    Args:
        user_in: User registration data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create user
    user = create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access + refresh tokens.
    
    Args:
        credentials: User login credentials
        db: Database session
        
    Returns:
        Access token, refresh token, and user information
        
    Raises:
        UnauthorizedException: If credentials are invalid
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Get user by email
    user = get_user_by_email(db, credentials.email)
    if not user:
        # Don't reveal if email exists - use generic error
        raise UnauthorizedException(detail="Incorrect email or password")
    
    # Check if user is active FIRST (security: check status before password verification)
    if not user.is_active:
        # Log failed login attempt for inactive user
        try:
            from app.db.crud.audit import create_audit_log
            from app.db.models.audit import AuditAction
            
            create_audit_log(
                db=db,
                action=AuditAction.LOGIN_FAILED,
                description=f"Login attempt by inactive user: {credentials.email}",
                user_id=user.id,
                resource_type="user",
                resource_id=user.id,
                success="failed",
                error_message="User account is inactive"
            )
        except Exception:
            pass  # Don't fail login if audit log fails
        
        logger.warning(f"Login attempt by inactive user: {credentials.email}")
        raise UnauthorizedException(detail="Account deactivated")
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        # Log failed login attempt
        try:
            from app.db.crud.audit import create_audit_log
            from app.db.models.audit import AuditAction
            
            create_audit_log(
                db=db,
                action=AuditAction.LOGIN_FAILED,
                description=f"Failed login attempt: incorrect password for {credentials.email}",
                user_id=user.id,
                resource_type="user",
                resource_id=user.id,
                success="failed",
                error_message="Incorrect password"
            )
        except Exception:
            pass
        
        raise UnauthorizedException(detail="Incorrect email or password")
    
    # Update last login
    update_last_login(db, user.id)
    
    # Log successful login (non-blocking)
    try:
        from app.db.crud.audit import create_audit_log
        from app.db.models.audit import AuditAction
        
        create_audit_log(
            db=db,
            action=AuditAction.LOGIN,
            description=f"User logged in: {user.email}",
            user_id=user.id,
            resource_type="user",
            resource_id=user.id
        )
    except Exception:
        pass  # Don't fail login if audit log fails
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=User.model_validate(user)
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    
    Args:
        token_data: Refresh token
        db: Database session
        
    Returns:
        New access token
        
    Raises:
        UnauthorizedException: If refresh token is invalid
    """
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)
    if not payload:
        raise UnauthorizedException(detail="Invalid refresh token")
    
    # Validate token type
    if payload.get("type") != "refresh":
        raise UnauthorizedException(detail="Invalid token type")
    
    # Get user ID
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException(detail="Invalid token payload")
    
    # Verify user exists and is active
    from app.db.crud.user import get_user
    from uuid import UUID
    
    try:
        user_id = UUID(user_id_str)
        user = get_user(db, user_id)
        if not user:
            raise UnauthorizedException(detail="User not found")
        if not user.is_active:
            raise UnauthorizedException(detail="Account deactivated")
    except ValueError:
        raise UnauthorizedException(detail="Invalid user ID in token")
    
    # Create new access token
    access_token = create_access_token(data={"sub": user_id_str})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    Note: With JWT tokens, server-side logout is handled by client
    discarding the token. This endpoint exists for consistency.
    
    For true logout, implement token blacklisting with Redis.
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return User.model_validate(current_user)


class PasswordResetByEmailRequest(BaseModel):
    """Schema for password reset by email."""
    email: str = Field(..., description="User email address")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")


@router.post("/reset-password-by-email")
async def reset_password_by_email(
    reset_data: PasswordResetByEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Reset user password by email (for login page).
    
    This endpoint allows users to reset their password directly from the login page
    by providing their email and new password. Same workflow as admin password reset.
    
    Args:
        reset_data: Email and new password
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        NotFoundException: If user not found
        BadRequestException: If user is inactive
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get user by email
        user = get_user_by_email(db, reset_data.email)
        if not user:
            logger.warning(f"Password reset attempted for non-existent email: {reset_data.email}")
            raise NotFoundException(detail="User not found")
        
        # Check if user is active (SECURITY: Must check before allowing password reset)
        if not user.is_active:
            logger.warning(f"SECURITY: Password reset attempted for inactive user: {reset_data.email}")
            
            # Audit log the failed attempt (non-blocking)
            try:
                from app.db.crud.audit import create_audit_log
                from app.db.models.audit import AuditAction
                
                create_audit_log(
                    db=db,
                    action=AuditAction.LOGIN_FAILED,  # Use LOGIN_FAILED as security event
                    description=f"Password reset attempt blocked for inactive user: {reset_data.email}",
                    user_id=user.id,
                    resource_type="user",
                    resource_id=user.id,
                    success="failed",
                    error_message="User account is inactive - password reset blocked"
                )
            except Exception as e:
                logger.warning(f"Failed to create audit log for blocked password reset: {str(e)}")
            
            raise BadRequestException(
                detail="Account deactivated. Please contact administrator."
            )
        
        # Update password
        try:
            updated = update_password(db, user.id, reset_data.new_password)
            if not updated:
                raise NotFoundException(detail="User not found")
            logger.info(f"Password reset successful for user: {reset_data.email}")
        except Exception as e:
            logger.error(f"Error updating password: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reset password: {str(e)}"
            )
        
        # Audit log (non-blocking - don't fail if it errors)
        try:
            from app.db.crud.audit import create_audit_log
            from app.db.models.audit import AuditAction
            
            create_audit_log(
                db=db,
                action=AuditAction.PASSWORD_CHANGED,
                description=f"Password reset by user via login page for '{updated.email}'",
                user_id=updated.id,
                resource_type="user",
                resource_id=updated.id
            )
        except Exception as e:
            # Log audit failure but don't fail the request
            logger.warning(f"Failed to create audit log (non-critical): {str(e)}")
            # Rollback any partial audit log transaction
            try:
                db.rollback()
            except Exception:
                pass
        
        return {"message": "Password reset successfully"}
        
    except (NotFoundException, BadRequestException, HTTPException):
        # Re-raise known exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in reset_password_by_email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
