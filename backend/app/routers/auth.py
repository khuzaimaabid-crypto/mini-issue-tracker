"""
Authentication Router
====================

This module handles user registration and login endpoints.

What This Does:
- POST /auth/register - Create new user account
- POST /auth/login - Login and get JWT token

Router vs Service vs Repository:
- Router (this file): Receives HTTP requests, returns HTTP responses
- Service (auth_service): Contains business logic (validation, password hashing)
- Repository: Talks to database (queries users table)

Why This Separation?
- Router = "What endpoints exist?" (HTTP layer)
- Service = "What rules apply?" (business logic layer)
- Repository = "How to get data?" (database layer)
- Makes code testable and maintainable

Flow Example (Registration):
    Client sends: POST /auth/register {"email": "user@test.com", "password": "pass123"}
    → Router validates JSON format (UserCreate schema)
    → Service checks email not taken, hashes password
    → Repository saves to database
    → Returns user data (without password)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.auth import Token
from app.services.auth import auth_service


# ═══════════════════════════════════════════════
# Router Configuration
# ═══════════════════════════════════════════════

# Creates a router with /auth prefix and "Authentication" tag for docs
# All routes in this file will be under /auth/* (e.g., /auth/register)
# Tags group endpoints in Swagger UI documentation
router = APIRouter(
    prefix="/auth",            # All routes start with /auth
    tags=["Authentication"]    # Groups these endpoints in API docs
)


# ═══════════════════════════════════════════════
# Registration Endpoint
# ═══════════════════════════════════════════════

@router.post("/register",
    response_model=UserResponse,              # Validates response matches UserResponse schema
    status_code=status.HTTP_201_CREATED       # Returns 201 (Created) instead of default 200 (OK)
)

def register(
    user_data: UserCreate,                    # Pydantic validates incoming JSON against UserCreate schema
    database_session: Session = Depends(get_db)  # FastAPI injects database session automatically
):
    """
    Register a new user account.
    
    What happens:
    1. FastAPI validates JSON matches UserCreate schema (email, password, name)
    2. Calls auth_service to handle business logic:
       - Check if email already exists
       - Hash the password (never store plain text!)
       - Create user in database
    3. Returns user data (without password) as UserResponse
    
    Request example:
        POST /auth/register
        {
            "email": "user@example.com",
            "password": "securepassword123",
            "name": "John Doe"
        }
    
    Response example (201 Created):
        {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe",
            "created_at": "2025-10-24T10:30:00Z"
        }
    
    Errors:
        400: Email already registered
        422: Invalid data format (missing fields, invalid email)
    """
    return auth_service.register(database_session, user_data)


# ═══════════════════════════════════════════════
# Login Endpoint
# ═══════════════════════════════════════════════

@router.post(
    "/login",
    response_model=Token  # Returns JWT token in format defined by Token schema
)
def login(
    credentials: UserLogin,                   # Pydantic validates JSON has email and password
    database_session: Session = Depends(get_db)  # Database session injected by FastAPI
):
    """
    Login user and receive JWT authentication token.
    
    What happens:
    1. FastAPI validates JSON matches UserLogin schema (email, password)
    2. Calls auth_service to handle authentication:
       - Find user by email
       - Verify password matches hashed version in database
       - Generate JWT token (contains user email, expires in 30 min)
    3. Returns JWT token for future authenticated requests
    
    Request example:
        POST /auth/login
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }
    
    Response example (200 OK):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    
    How to use the token:
        Send in Authorization header for protected endpoints:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    
    Errors:
        401: Invalid email or password
        422: Invalid data format (missing email/password)
    """
    return auth_service.login(database_session, credentials.email, credentials.password)