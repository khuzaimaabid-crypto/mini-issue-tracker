"""
Base Repository Pattern
=======================

Generic repository providing CRUD operations for all models.
Each model (User, Project, Issue) gets its own repository that inherits from this.

Why repositories? Separates database logic from business logic (services).
"""

from sqlalchemy.orm import Session


class BaseRepository:
    """
    Base class for all repositories.
    
    Provides common CRUD operations that work with any SQLAlchemy model.
    Child classes inherit these methods automatically.
    """
    
    def __init__(self):
        """
        Base repository constructor.
        
        It is the CHILD's responsibility to set 'self.model'.
        """
        pass

    def get_by_id(self, db, id):
        """
        Get a single record by ID.
        SQL: SELECT * FROM table WHERE id = {id} LIMIT 1
        
        Returns:
            Model instance or None if not found
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db, skip=0, limit=100):
        """
        Get all records with pagination.
        SQL: SELECT * FROM table OFFSET {skip} LIMIT {limit}
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum records to return
        
        Returns:
            List of model instances
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db, obj_in):
        """
        Create a new record.
        
        Args:
            obj_in: Dictionary with field values {"field": "value"}
        
        Steps:
            1. Create model instance from dict
            2. Add to session (staged, not saved yet)
            3. Commit (execute INSERT and save to DB)
            4. Refresh (reload to get auto-generated values like id, timestamps)
        
        Returns:
            Created model instance with all fields populated
        """
        db_obj = self.model(**obj_in)  # Unpack dict: User(email="...", password="...")
        db.add(db_obj)  # Stage for insertion
        db.commit()  # Execute: INSERT INTO table (...) VALUES (...)
        db.refresh(db_obj)  # Reload to get id, created_at, etc.
        return db_obj
    
    def update(self, db, db_obj, obj_in):
        """
        Update an existing record.
        
        Args:
            db_obj: Existing model instance from database
            obj_in: Dictionary with fields to update (can be partial)
        
        Steps:
            1. Loop through each field in obj_in
            2. Set attribute on db_obj (setattr modifies the object)
            3. Commit changes (execute UPDATE)
            4. Refresh to get updated timestamps
        
        Returns:
            Updated model instance
        """
        for field, value in obj_in.items():
            if value is not None:  # Only update if value was actually provided
                setattr(db_obj, field, value)  # db_obj.field = value
        db.commit()  # Execute: UPDATE table SET field=value WHERE id=...
        db.refresh(db_obj)  # Reload to get updated_at timestamp
        return db_obj
    
    def delete(self, db, id):
        """
        Delete a record by ID.
        SQL: DELETE FROM table WHERE id = {id}
        
        Steps:
            1. Find the record
            2. Delete it from session
            3. Commit (execute DELETE)
        
        Returns:
            True if deleted, False if not found
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)  # Stage for deletion
            db.commit()  # Execute DELETE query
            return True
        return False