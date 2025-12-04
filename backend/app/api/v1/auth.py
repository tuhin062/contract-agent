"""
Authentication endpoints for login, logout, and token refresh.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.db.crud.user import get_user_by_email, update_last_login, create_user
from app.schemas.user import UserLogin, Token, TokenRefresh, User, UserCreate
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.errors import UnauthorizedException
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
    # Get user by email
    user = get_user_by_email(db, credentials.email)
    if not user:
        raise UnauthorizedException(detail="Incorrect email or password")
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException(detail="Incorrect email or password")
    
    # Check if user is active
    if not user.is_active:
        raise UnauthorizedException(detail="User account is inactive")
    
    # Update last login
    update_last_login(db, user.id)
    
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
