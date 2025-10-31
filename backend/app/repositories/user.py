"""
User Repository - Database operations for User model

Extends BaseRepository with user-specific queries (get by email).
Inherits common CRUD methods: get_by_id(), update(), delete()
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """User-specific database operations"""
    
    def __init__(self):
        
        """Initialize by setting the 'self.model' attribute directly."""
        self.model = User

    def get_by_email(self, db, email):
        """
        Find user by email address (used for login and checking duplicates).
        SQL: SELECT * FROM users WHERE email = ?
        """
        return db.query(User).filter(User.email == email).first()
    
    def create_user(self, db, name, email, hashed_password):
        """
        Create new user with hashed password.
        Uses parent's create() method with a dictionary.
        """
        return self.create(db, {  # Calls BaseRepository.create()
            "name": name,
            "email": email,
            "hashed_password": hashed_password
        })


# Singleton instance
user_repository = UserRepository()