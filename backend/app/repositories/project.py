"""
Project Repository - Database operations for Project model

Extends BaseRepository with project-specific queries (get user's projects, count issues).
Inherits common CRUD methods: get_by_id(), update(), delete()
"""

from sqlalchemy.orm import Session
from sqlalchemy import func  # SQL aggregate functions (COUNT, SUM, etc.)
from app.models.project import Project
from app.models.issue import Issue
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository):
    """Project-specific database operations"""
    
    def __init__(self):
        
        """Initialize by setting the 'self.model' attribute directly."""
        self.model = Project

    def get_user_projects(self, db, user_id):
        """
        Get all projects owned by a user.
        
        Custom query - filters by created_by (can't use generic get_all()).
        
        SQL: SELECT * FROM projects WHERE created_by = {user_id}
        
        Returns:
            List of Project instances owned by the user
        """
        return db.query(Project).filter(Project.created_by == user_id).all()
    
    def get_user_projects_with_count(self, db, user_id):
        """
        Get user's projects with count of issues in each project.
        
        Custom query that joins projects with issues and aggregates count.
        Can't use generic get_all() because of the JOIN and COUNT.
        
        SQL: 
        SELECT projects.*, COUNT(issues.id) as issue_count 
        FROM projects 
        LEFT JOIN issues ON projects.id = issues.project_id 
        WHERE projects.created_by = {user_id} 
        GROUP BY projects.id
        
        Returns:
            List of dictionaries with project data + issue_count
        """
        results = (
            db.query(Project, func.count(Issue.id).label("issue_count"))
            .outerjoin(Issue, Project.id == Issue.project_id)  # LEFT JOIN issues
            .filter(Project.created_by == user_id)
            .group_by(Project.id)
            .all()
        )
        
        # Convert to list of dicts
        return [
            {
                **proj.__dict__,  # Spread all project fields
                "issue_count": count  # Add aggregated count
            }
            for proj, count in results
        ]
    
    def create_project(self, db, name, description, user_id):
        """
        Create new project.
        
        Wrapper for create() with project-specific fields.
        Maps function parameters to database columns.
        
        Args:
            name: Project name
            description: Project description (optional)
            user_id: ID of user creating the project
        
        Returns:
            Created Project instance with id, timestamps
        """
        return self.create(db, {
            "name": name,
            "description": description,
            "created_by": user_id
        })


# Singleton instance
project_repository = ProjectRepository()