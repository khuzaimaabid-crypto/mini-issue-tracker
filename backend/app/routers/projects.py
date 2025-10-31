"""
Projects Router - Manage user projects

Endpoints:
- GET /projects - List all user's projects
- GET /projects/{id} - Get single project
- POST /projects - Create project
- PATCH /projects/{id} - Update project (partial)
- DELETE /projects/{id} - Delete project (permanent)

Note: Users can only see/modify their own projects
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.auth_deps import auth
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project import project_service


# ═══════════════════════════════════════════════
# Router Configuration
# ═══════════════════════════════════════════════

router = APIRouter(prefix="/projects", tags=["Projects"])


# ═══════════════════════════════════════════════
# List User's Projects
# ═══════════════════════════════════════════════

@router.get("", response_model=List[ProjectResponse])
def get_projects(
    database_session: Session = Depends(get_db),          # Database session (injected by FastAPI)
    current_user: User = Depends(auth)                     # Logged-in user (extracted from JWT, injected by FastAPI)
):
    """
    Get all projects owned by the authenticated user.
    
    Flow: Extract user from JWT → SELECT FROM projects WHERE owner_id = current_user.id → Return list
    
    Example: GET /projects

    Returns: List of Projects
    [{"id": 1, "name": "Website", "description": "...", "owner_id": 5, "created_at": "..."}]
    """
    return project_service.get_user_projects(database_session, current_user)


# ═══════════════════════════════════════════════
# Get Single Project
# ═══════════════════════════════════════════════

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,                                       # From URL path: /projects/5
    database_session: Session = Depends(get_db),
    current_user: User = Depends(auth)
):
    """
    Get single project by ID (must be owner).
    
    Flow: SELECT FROM projects WHERE id=X → Verify owner_id = current_user.id → Return project
    
    Returns: ProjectResponse with all fields
    Errors: 403 (not owner), 404 (not found)
    """
    return project_service.get_project(database_session, project_id, current_user)


# ═══════════════════════════════════════════════
# Create Project
# ═══════════════════════════════════════════════

@router.post("", 
    response_model=ProjectResponse, 
    status_code=status.HTTP_201_CREATED  # 201 = resource created successfully
)
def create_project(
    project_data: ProjectCreate,                           # From request body (FastAPI validates JSON against ProjectCreate schema)
    database_session: Session = Depends(get_db),
    current_user: User = Depends(auth)
):
    """
    Create new project owned by current user.
    
    Flow: Validate JSON → INSERT INTO projects (owner_id = current_user.id) → Return with auto-generated ID
    
    Request: {"name": "Website", "description": "Company site"} (name required, description optional)
    Response: Same fields + id (auto-generated), owner_id, created_at (auto-set)
    Errors: 422 (invalid data, e.g., missing name)
    """
    return project_service.create_project(database_session, project_data, current_user)


# ═══════════════════════════════════════════════
# Update Project
# ═══════════════════════════════════════════════

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,                                       # From URL path
    project_data: ProjectUpdate,                           # From request body (FastAPI validates, all fields optional - partial update)
    database_session: Session = Depends(get_db),
    current_user: User = Depends(auth)
):
    """
    Update project (partial - only send fields you want to change).
    
    Flow: Validate JSON → Fetch project → Verify owner → UPDATE only provided fields → Set updated_at
    
    Request: {"name": "New Name"} or {"description": "Updated desc"} etc.
    Response: Full updated project with new updated_at timestamp
    Errors: 403 (not owner), 404 (not found), 422 (invalid values)
    """
    return project_service.update_project(database_session, project_id, project_data, current_user)


# ═══════════════════════════════════════════════
# Delete Project
# ═══════════════════════════════════════════════

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,                                       # From URL path
    database_session: Session = Depends(get_db),
    current_user: User = Depends(auth)
):
    """
    Delete project permanently (cannot be undone, also deletes all issues in it).
    
    Flow: Fetch project → Verify owner → CASCADE DELETE (removes all issues) → DELETE FROM projects
    
    Returns: Empty response with 204 status (success, no content)
    Errors: 403 (not owner), 404 (not found)
    Warning: This deletes the project AND all its issues permanently
    """
    project_service.delete_project(database_session, project_id, current_user)
    return None  # FastAPI converts to 204 No Content