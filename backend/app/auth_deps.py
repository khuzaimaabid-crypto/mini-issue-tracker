"""
Authentication Dependencies - FastAPI dependency for JWT authentication
Provides class-based authentication checking for protected routes.
"""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.token_handler import token_handler
from app.utils.exceptions import UnauthorizedException


class Auth:
    """
    FastAPI dependency class for JWT authentication.
    
    Extracts JWT token from Authorization header, verifies it,
    and returns the authenticated user from the database.
    
    Usage in routes:
        auth = Auth()

        @router.get("/projects")
        def get_projects(current_user: User = Depends(auth)):
            return current_user.projects
    
    Flow:
        Request with "Authorization: Bearer <token>"
        → Extract token
        → Decode & verify token
        → Get user email from token
        → Query user from database
        → Return User object
    """
    
    def __init__(self):
        """
        Initialize authentication dependency.
        
        HTTPBearer automatically extracts "Bearer <token>" from Authorization header.
        """
        self._token_extractor = HTTPBearer()
    
    async def __call__(
        self,
        auth_header: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        database_session: Session = Depends(get_db)
    ) -> User:
        """
        Authenticate request and return the current user.
        
        Called automatically by FastAPI when route uses Depends(auth).
        This is the magic method that makes the class callable as a dependency.
        
        Args:
            auth_header: Contains JWT token from "Authorization: Bearer <token>"
            database_session: Database session for querying user
            
        Returns:
            Authenticated User object from database
            
        Raises:
            UnauthorizedException (401): If token invalid/expired or user not found
        """
        # Extract the actual token string (the "eyJhbGc..." part)
        jwt_token = auth_header.credentials
        
        # Decode the JWT token to get the payload
        payload = token_handler.decode_token(jwt_token)
        if payload is None:
            raise UnauthorizedException(detail="Invalid authentication token")
        
        # Get user's email from the token payload
        # "sub" (subject) is the standard JWT field for user identifier
        user_email: str = payload.get("sub")
        if user_email is None:
            raise UnauthorizedException(detail="Invalid token payload")
        
        # Look up user in database by email
        # Ensures user still exists (not deleted after token was issued)
        user = database_session.query(User).filter(User.email == user_email).first()
        if user is None:
            raise UnauthorizedException(detail="User not found")
        
        # Return the authenticated user
        return user


# ═══════════════════════════════════════════════
# Singleton Instance - Shared across routes
# ═══════════════════════════════════════════════
# Create single instance to use in all route dependencies
# Usage: current_user: User = Depends(auth)
auth = Auth()