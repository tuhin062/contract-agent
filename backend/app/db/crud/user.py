"""
CRUD operations for User model.
Handles user creation, retrieval, update, and deletion.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None
) -> List[User]:
    """
    Get list of users with optional filters.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        role: Filter by role
        is_active: Filter by active status
    """
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()


def get_users_count(
    db: Session,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None
) -> int:
    """Get total count of users with optional filters."""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.count()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        user: User creation data
        
    Returns:
        Created user instance
    """
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    db_user = User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        role=user.role,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session,
    user_id: UUID,
    user_update: UserUpdate
) -> Optional[User]:
    """
    Update user information.
    
    Args:
        db: Database session
        user_id: User ID
        user_update: Update data
        
    Returns:
        Updated user or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def update_password(
    db: Session,
    user_id: UUID,
    new_password: str
) -> Optional[User]:
    """
    Update user's password.
    
    Args:
        db: Database session
        user_id: User ID
        new_password: New plain text password
        
    Returns:
        Updated user or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.password_hash = get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_last_login(db: Session, user_id: UUID) -> Optional[User]:
    """
    Update user's last login timestamp.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Updated user or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def deactivate_user(db: Session, user_id: UUID) -> Optional[User]:
    """
    Deactivate a user (soft delete).
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Deactivated user or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user


def activate_user(db: Session, user_id: UUID) -> Optional[User]:
    """
    Activate a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Activated user or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID) -> bool:
    """
    Permanently delete a user (hard delete).
    Use with caution - prefer deactivate_user for soft delete.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        True if deleted, False if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def search_users(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Search users by name or email.
    
    Args:
        db: Database session
        query: Search query string
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of matching users
    """
    search_pattern = f"%{query}%"
    return db.query(User).filter(
        (User.name.ilike(search_pattern)) | 
        (User.email.ilike(search_pattern))
    ).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
