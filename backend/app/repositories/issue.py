"""
Issue Repository - Database operations for Issue model

Extends BaseRepository with issue-specific queries (filtering by project, status, priority).
Inherits common CRUD methods: get_by_id(), update(), delete()
"""

from sqlalchemy.orm import Session
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.repositories.base import BaseRepository


class IssueRepository(BaseRepository):
    """Issue-specific database operations"""
    
    def __init__(self):
        
        """Initialize by setting the 'self.model' attribute directly."""
        self.model = Issue
    
    def get_project_issues(self, db, project_id, status=None, priority=None):
        """
        Get all issues for a project with optional filtering.
        
        Custom query with conditional WHERE clauses based on filters.
        Can't use generic get_all() because of the filtering logic.
        
        SQL: SELECT * FROM issues WHERE project_id = {project_id} 
             [AND status = {status}] [AND priority = {priority}]
        
        Args:
            project_id: Filter by project
            status: Optional - filter by status (Open, In Progress, Closed)
            priority: Optional - filter by priority (Low, Medium, High)
        
        Returns:
            List of Issue instances
        """
        query = db.query(Issue).filter(Issue.project_id == project_id)
        
        # Add optional filters (if provided)
        if status:
            query = query.filter(Issue.status == status)
        if priority:
            query = query.filter(Issue.priority == priority)
        
        return query.order_by(Issue.created_at.desc()).all()
    
    def create_issue(self, db, project_id, title, description, status, priority, user_id):
        """
        Create new issue in a project.
        
        Wrapper for create() with issue-specific fields.
        Maps function parameters to database columns.
        
        Args:
            project_id: ID of parent project
            title: Issue title/summary
            description: Detailed description
            status: IssueStatus enum (Open, In Progress, Closed)
            priority: IssuePriority enum (Low, Medium, High)
            user_id: ID of user creating the issue
        
        Returns:
            Created Issue instance with id, timestamps
        """
        return self.create(db, {
            "project_id": project_id,
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "created_by": user_id
        })


# Singleton instance
issue_repository = IssueRepository()