"""
Issue Service - Business logic for issue (task/bug) management

Handles issue CRUD operations with project ownership validation.
Users can only manage issues in projects they own.

Flow: Router → Service (authorization/validation) → Repository (database) → Database
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.issue import IssueStatus, IssuePriority
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse
from app.repositories.project import project_repository
from app.repositories.issue import issue_repository
from app.utils.exceptions import NotFoundException, ForbiddenException


class IssueService:
    """Manages issue operations with project ownership checks"""
    
    def get_project_issues(
        self,
        database_session: Session,
        project_id: int,
        user: User,
        status: Optional[IssueStatus] = None,
        priority: Optional[IssuePriority] = None
    ) -> List[IssueResponse]:
        """
        Get all issues in a project with optional status/priority filters.
        
        Flow: Verify project ownership → SELECT issues WHERE project_id=X → Apply filters → Return
        Raises: NotFoundException(404), ForbiddenException(403)
        """
        # Verify project exists and user owns it
        project = project_repository.get_by_id(database_session, project_id)
        if not project:
            raise NotFoundException(detail="Project not found")
        
        if project.created_by != user.id:
            raise ForbiddenException(detail="You don't have access to this project")
        
        # Fetch issues with optional filters (status AND/OR priority)
        issues = issue_repository.get_project_issues(database_session, project_id, status, priority)
        return [IssueResponse.model_validate(i) for i in issues]
    
    def get_issue(self, database_session: Session, issue_id: int, user: User) -> IssueResponse:
        """
        Get single issue with project ownership verification.
        
        Flow: Fetch issue → Verify project owner → Return
        Raises: NotFoundException(404), ForbiddenException(403)
        """
        # Fetch issue from database
        issue = issue_repository.get_by_id(database_session, issue_id)
        
        if not issue:
            raise NotFoundException(detail="Issue not found")
        
        # Verify user owns the parent project (issues inherit project permissions)
        project = project_repository.get_by_id(database_session, issue.project_id)
        if project.created_by != user.id:
            raise ForbiddenException(detail="You don't have access to this issue")
        
        return IssueResponse.model_validate(issue)
    
    def create_issue(
        self,
        database_session: Session,
        project_id: int,
        issue_data: IssueCreate,
        user: User
    ) -> IssueResponse:
        """
        Create new issue in a project with ownership verification.
        
        Flow: Verify project ownership → INSERT INTO issues → Return with auto-generated ID
        Raises: NotFoundException(404), ForbiddenException(403)
        """
        # Verify project exists and user owns it
        project = project_repository.get_by_id(database_session, project_id)
        if not project:
            raise NotFoundException(detail="Project not found")
        
        if project.created_by != user.id:
            raise ForbiddenException(detail="You don't have permission to create issues in this project")
        
        # Create issue in database
        issue = issue_repository.create_issue(
            db=database_session,
            project_id=project_id,
            title=issue_data.title,
            description=issue_data.description,
            status=issue_data.status,
            priority=issue_data.priority,
            user_id=user.id
        )
        
        return IssueResponse.model_validate(issue)
    
    def update_issue(
        self,
        database_session: Session,
        issue_id: int,
        issue_data: IssueUpdate,
        user: User
    ) -> IssueResponse:
        """
        Update issue with project ownership verification (partial update).
        
        Flow: Fetch issue → Verify project owner → UPDATE only provided fields → Return
        Raises: NotFoundException(404), ForbiddenException(403)
        """
        issue = issue_repository.get_by_id(database_session, issue_id)
        
        if not issue:
            raise NotFoundException(detail="Issue not found")
        
        # Verify user owns the parent project
        project = project_repository.get_by_id(database_session, issue.project_id)
        if project.created_by != user.id:
            raise ForbiddenException(detail="You don't have permission to update this issue")
        
        # Extract only fields that were actually provided (exclude_unset=True ignores None values)
        update_data = issue_data.model_dump(exclude_unset=True)
        updated_issue = issue_repository.update(database_session, issue, update_data)
        
        return IssueResponse.model_validate(updated_issue)
    
    def delete_issue(self, database_session: Session, issue_id: int, user: User) -> bool:
        """
        Delete issue permanently with project ownership verification.
        
        Flow: Fetch issue → Verify project owner → DELETE FROM issues
        Raises: NotFoundException(404), ForbiddenException(403)
        """
        issue = issue_repository.get_by_id(database_session, issue_id)
        
        if not issue:
            raise NotFoundException(detail="Issue not found")
        
        # Verify user owns the parent project
        project = project_repository.get_by_id(database_session, issue.project_id)
        if project.created_by != user.id:
            raise ForbiddenException(detail="You don't have permission to delete this issue")
        
        # Permanently delete issue
        return issue_repository.delete(database_session, issue_id)


# ═══════════════════════════════════════════════
# Singleton Instance
# ═══════════════════════════════════════════════
issue_service = IssueService()