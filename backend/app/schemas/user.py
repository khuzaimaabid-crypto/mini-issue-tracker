"""
User Schemas
============

Pydantic models for user data validation (registration, login, responses).

Schema purpose:
- Define what fields are required/optional in requests
- Validate data types and formats (email format, string length, etc.)
- Control what data is returned in responses (hide passwords)
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Base user fields shared across multiple schemas.
    
    Inherited by: UserCreate, UserResponse, UserInDB
    Contains: Common fields that appear in both requests and responses
    """
    email: EmailStr                                  # Auto-validates email format (e.g., "user@example.com")
    name: str = Field(..., min_length=2, max_length=100)  # ... = required field


class UserCreate(UserBase):
    """
    Schema for user registration request.
    
    Used by: POST /auth/register
    Validates: Email format, name length (2-100), password length (6-100)
    """
    password: str = Field(..., min_length=6, max_length=100)  # Plain text password (will be hashed)


class UserLogin(BaseModel):
    """
    Schema for user login request.
    
    Used by: POST /auth/login
    Validates: Email format and password presence
    """
    email: EmailStr
    password: str  # Plain text password for verification


class UserResponse(UserBase):
    """
    Schema for user data in API responses.
    
    Returned by: GET endpoints, successful registration
    Excludes: Password/hashed_password (security)
    """
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)  # Allows conversion from SQLAlchemy model


class UserInDB(UserBase):
    """
    Schema representing full user data in database.
    
    Used internally by: Repositories when fetching from database
    Includes: All fields including hashed password
    """
    id: int
    hashed_password: str  # Bcrypt hash (never returned in API responses)
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Allows conversion from SQLAlchemy model