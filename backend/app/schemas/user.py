"""
User Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional
from datetime import datetime
from app.db.models.user import UserRole


# Base schema with common attributes
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


# Schema for creating a user
class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.REGULAR


# Schema for updating a user
class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# Schema for user in database (response)
class User(UserBase):
    """Schema for user response."""
    model_config = {"from_attributes": True}  # Pydantic v2 (was orm_mode in v1)
    
    id: UUID4
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


# Schema for authentication
class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


# Schema for token response
class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User


# Schema for token refresh
class TokenRefresh(BaseModel):
    """Schema for refreshing access token."""
    refresh_token: str


# Schema for token payload
class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: str  # Subject (user ID)
    exp: int  # Expiration timestamp
    type: str  # Token type (access/refresh)
