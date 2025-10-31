"""
Authentication Service - Handles user registration and login

Business logic layer between routers and repositories.
Validates user credentials, hashes passwords, generates JWT tokens.

Flow: Router → Service (validation/logic) → Repository (database) → Database
"""

from datetime import timedelta
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.repositories.user import user_repository
from app.auth.password_handler import password_handler
from app.auth.token_handler import token_handler
from app.utils.exceptions import BadRequestException, UnauthorizedException, ConflictException
from app.config import settings


class AuthService:
    """Handles user authentication: registration and login"""
    
    def register(self, database_session: Session, user_data: UserCreate) -> UserResponse:
        """
        Register new user with hashed password.
        
        Flow: Check email exists → Hash password → INSERT INTO users → Return user
        Raises: ConflictException(409) if email already registered
        """
        # Check if email already taken (SELECT FROM users WHERE email=X)
        existing_user = user_repository.get_by_email(database_session, user_data.email)
        if existing_user:
            raise ConflictException(detail="Email already registered")
        
        # Hash password using bcrypt (one-way encryption, cannot be reversed)
        hashed_password = password_handler.hash(user_data.password)
        
        # Create user in database with hashed password
        user = user_repository.create_user(
            db=database_session,
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        # Convert SQLAlchemy model to Pydantic response schema
        return UserResponse.model_validate(user)
    
    def login(self, database_session: Session, email: str, password: str) -> Token:
        """
        Authenticate user and return JWT token.
        
        Flow: Find user by email → Verify password → Generate JWT → Return token
        Raises: UnauthorizedException(401) if email/password invalid
        """
        # Fetch user from database (SELECT FROM users WHERE email=X)
        user = user_repository.get_by_email(database_session, email)
        if not user:
            raise UnauthorizedException(detail="Invalid email or password")
        
        # Verify password matches hashed version (uses bcrypt.checkpw)
        if not password_handler.verify(password, user.hashed_password):
            raise UnauthorizedException(detail="Invalid email or password")
        
        # Create JWT token with user info, expires in 30 minutes (from settings)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = token_handler.create_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token)


# ═══════════════════════════════════════════════
# Singleton Instance
# ═══════════════════════════════════════════════
# Single instance shared across the app (no need to create multiple instances)
auth_service = AuthService()