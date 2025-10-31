"""
Password Handler - Secure password hashing and verification
Handles all password-related security operations using bcrypt.
"""
from passlib.context import CryptContext


class PasswordHandler:
    """
    Manages password hashing and verification using bcrypt.
    
    Bcrypt is intentionally slow to prevent brute-force attacks.
    Hashes are one-way: you cannot reverse them to get the original password.
    
    Usage:
        password_handler = PasswordHandler()
        hashed = password_handler.hash("mypassword123")
        is_valid = password_handler.verify("mypassword123", hashed)
    """
    
    def __init__(self):
        """
        Initialize password context with bcrypt algorithm.
        
        CryptContext handles the hashing algorithm configuration.
        - schemes=["bcrypt"]: Use bcrypt algorithm
        - deprecated="auto": Automatically rehash passwords using old algorithms
        """
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash(self, plain_password: str) -> str:
        """
        Hash a plain text password for secure storage.
        
        Creates one-way bcrypt hash that cannot be reversed.
        Same password always produces different hash (due to salt).
        
        Args:
            plain_password: The plain text password to hash
            
        Returns:
            Hashed password string (e.g., "$2b$12$xyz...")
            
        Example:
            >>> handler = PasswordHandler()
            >>> hashed = handler.hash("mypassword123")
            >>> print(hashed)
            $2b$12$KIXqF5zJ9Z8qvZ5Z5Z5Z5u...
        """
        return self._pwd_context.hash(plain_password)
    
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.
        
        Securely compares without exposing the hash or timing information.
        Used during login to check if provided password matches stored hash.
        
        Args:
            plain_password: The plain text password to check
            hashed_password: The hashed password from database
            
        Returns:
            True if password matches, False otherwise
            
        Example:
            >>> handler = PasswordHandler()
            >>> hashed = handler.hash("mypassword123")
            >>> handler.verify("mypassword123", hashed)
            True
            >>> handler.verify("wrongpassword", hashed)
            False
        """
        return self._pwd_context.verify(plain_password, hashed_password)


# ═══════════════════════════════════════════════
# Singleton Instance - Shared across the app
# ═══════════════════════════════════════════════
# Single instance to avoid recreating CryptContext multiple times
password_handler = PasswordHandler()