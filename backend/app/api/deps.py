"""
Dependency injection for API endpoints.
Provides reusable dependencies for database sessions, authentication, etc.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.db.crud.user import get_user
from app.core.security import decode_token
from app.core.errors import UnauthorizedException, ForbiddenException
from app.db.models.user import User, UserRole
from app.schemas.user import TokenPayload

# Security scheme for Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials with Bearer token
        db: Database session
        
    Returns:
        Current user instance
        
    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException(detail="Invalid authentication token")
    
    # Validate token type
    if payload.get("type") != "access":
        raise UnauthorizedException(detail="Invalid token type")
    
    # Get user ID from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException(detail="Invalid token payload")
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException(detail="Invalid user ID in token")
    
    # Get user from database
    user = get_user(db, user_id)
    if not user:
        raise UnauthorizedException(detail="User not found")
    
    if not user.is_active:
        raise UnauthorizedException(detail="User account is inactive")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (already validated in get_current_user)."""
    return current_user


def require_role(required_roles: list[UserRole]):
    """
    Dependency factory to require specific user roles.
    
    Args:
        required_roles: List of roles that are allowed
        
    Returns:
        Dependency function that validates user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise ForbiddenException(
                detail=f"This action requires one of the following roles: {', '.join([r.value for r in required_roles])}"
            )
        return current_user
    
    return role_checker


# Convenience dependencies for specific roles
require_admin = require_role([UserRole.ADMIN])
require_reviewer = require_role([UserRole.REVIEWER, UserRole.ADMIN])
