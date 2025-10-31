"""
Project Service - Business logic for project management

Handles project CRUD operations with ownership validation.
Only project owners can view/modify their projects.

Flow: Router → Service (authorization/validation) → Repository (database) → Database
"""

from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.repositories.project import project_repository
from app.utils.exceptions import NotFoundException, ForbiddenException


class ProjectService:
    """Manages project operations with ownership checks"""
    
    def get_user_projects(self, database_session: Session, user: User) -> List[ProjectResponse]:
        """
        Get all projects owned by the user.
        
        Flow: SELECT FROM projects WHERE owner_id=user.id → Convert to response schemas
        """
        projects = project_repository.get_user_projects(database_session, user.id)
        return [ProjectResponse.model_validate(p) for p in projects]
    
    def get_project(self, database_session: Session, project_id: int, user: User) -> ProjectResponse:
        """
        Get single project with ownership verification.
        
        Flow: Fetch project → Verify owner → Return
        Raises: NotFoundException(404), ForbiddenException(403)
        """
        # Fetch from database (SELECT FROM projects WHERE id=X)
        project = project_repository.get_by_id(database_session, project_id)
        
        if not project:
            raise NotFoundException(detail="Project not found")
        
        # Verify ownership (only owner can view)
        if project.created_by != user.id:
            raise ForbiddenException(detail="You don't have access to this project")
        
        return ProjectResponse.model_validate(project)
    
    def create_project(self, database_session: Session, project_data: ProjectCreate, user: User) -> ProjectResponse:
        """
        Create new project owned by the user.
        
        Flow: INSERT INTO projects (owner_id=user.id) → Return with auto-generated ID
        """
        project = project_repository.create_project(
            db=database_session,
            name=project_data.name,
            description=project_data.description,
            user_id=user.id
        )
        
        return ProjectResponse.model_validate(project)
    
    def update_project(
        self,
        database_session: Session,
        project_id: int,
        project_data: ProjectUpdate,
        user: User
    ) -> ProjectResponse:
        """
        Update project with ownership verification (partial update).
        
        Flow: Fetch project → Verify owner → UPDATE only provided fields → Return
        Raises: NotFoundException(404), ForbiddenException(403)
        """
        project = project_repository.get_by_id(database_session, project_id)
        
        if not project:
            raise NotFoundException(detail="Project not found")
        
        # Verify ownership (only owner can update)
        if project.created_by != user.id:
            raise ForbiddenException(detail="You don't have permission to update this project")
        
        # Extract only fields that were actually provided (exclude_unset=True ignores None values)
        update_data = project_data.model_dump(exclude_unset=True)
        updated_project = project_repository.update(database_session, project, update_data)
        
        return ProjectResponse.model_validate(updated_project)
    
    def delete_project(self, database_session: Session, project_id: int, user: User) -> bool:
        """
        Delete project permanently with ownership verification.
        
        Flow: Fetch project → Verify owner → CASCADE DELETE (removes all issues) → DELETE project
        Raises: NotFoundException(404), ForbiddenException(403)
        """
        project = project_repository.get_by_id(database_session, project_id)
        
        if not project:
            raise NotFoundException(detail="Project not found")
        
        # Verify ownership (only owner can delete)
        if project.created_by != user.id:
            raise ForbiddenException(detail="You don't have permission to delete this project")
        
        # Delete project (CASCADE will also delete all associated issues)
        return project_repository.delete(database_session, project_id)


# ═══════════════════════════════════════════════
# Singleton Instance
# ═══════════════════════════════════════════════
project_service = ProjectService()