"""
Authentication Schemas
======================

Pydantic models for JWT token handling (request/response validation).

Key difference from SQLAlchemy models:
- Pydantic schemas = Data validation for API (JSON → Python objects)
- SQLAlchemy models = Database tables (Python objects → SQL rows)

Flow: Request JSON → Pydantic validates → Service logic → SQLAlchemy saves to DB
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """
    JWT token response after successful login.
    
    Returned by: POST /auth/login
    Contains: Encoded JWT string and token type for Authorization header
    """
    access_token: str            # JWT string (e.g., "eyJhbGciOiJIUzI1NiIs...")
    token_type: str = "bearer"   # Always "bearer" for Bearer token authentication


class TokenData(BaseModel):
    """
    Decoded JWT payload data extracted from token.

    Used internally by: decode_token() in token_handler.py
    Contains: User identification info embedded in the JWT
    """
    email: Optional[str] = None     # User's email from token payload
    user_id: Optional[int] = None   # User's ID from token payload