"""
Token Handler - JWT token creation and verification
Handles all JWT (JSON Web Token) operations for authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings


class TokenHandler:
    """
    Manages JWT token creation and decoding for authentication.
    
    JWT tokens contain user data + expiration, signed with a secret key.
    Structure: header.payload.signature (three parts separated by dots)
    
    Usage:
        token_handler = TokenHandler()
        token = token_handler.create_token({"sub": "user@email.com", "user_id": 5})
        payload = token_handler.decode_token(token)
    """
    
    def __init__(self, secret_key: str = None, algorithm: str = None, default_expire_minutes: int = None):
        """
        Initialize token handler with configuration.
        
        Args:
            secret_key: Secret key for signing tokens (from settings if not provided)
            algorithm: JWT algorithm to use (default: HS256)
            default_expire_minutes: Default token expiration time in minutes
        """
        self._secret_key = secret_key or settings.SECRET_KEY
        self._algorithm = algorithm or settings.ALGORITHM
        self._default_expire_minutes = default_expire_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token with user data and expiration.
        
        Encodes user information into a signed token that can be verified later.
        The token is signed with SECRET_KEY so it cannot be tampered with.
        
        Args:
            data: Dictionary of claims to encode (e.g., {"sub": email, "user_id": 5})
            expires_delta: Custom expiration duration (uses default if None)
            
        Returns:
            JWT token string (e.g., "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
            
        Example:
            >>> handler = TokenHandler()
            >>> token = handler.create_token({"sub": "user@example.com", "user_id": 42})
            >>> print(token)
            eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV...
        """
        # Copy data to avoid modifying original
        to_encode = data.copy()
        
        # Calculate expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self._default_expire_minutes)
        
        # Add expiration claim to payload
        to_encode.update({"exp": expire})
        
        # Encode: data + SECRET_KEY → signed JWT string
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[dict]:
        """
        Decode and verify a JWT token, extracting the payload.
        
        Verifies the token signature using SECRET_KEY and checks expiration.
        Returns None if token is invalid, expired, or has wrong signature.
        
        Args:
            token: JWT token string to decode
            
        Returns:
            Payload dictionary (e.g., {"sub": email, "user_id": 5, "exp": ...})
            Returns None if token is invalid or expired
            
        Example:
            >>> handler = TokenHandler()
            >>> token = handler.create_token({"sub": "user@example.com"})
            >>> payload = handler.decode_token(token)
            >>> print(payload["sub"])
            user@example.com
        """
        try:
            # Decode: JWT string + SECRET_KEY → original payload (if valid)
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except JWTError:
            # Invalid signature, expired token, or malformed JWT
            return None


# ═══════════════════════════════════════════════
# Singleton Instance - Shared across the app
# ═══════════════════════════════════════════════
# Single instance configured with app settings
token_handler = TokenHandler()