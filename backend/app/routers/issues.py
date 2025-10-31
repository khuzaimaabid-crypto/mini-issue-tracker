"""
Issues Router - Manage tasks/bugs within projects

Endpoints:
- GET /projects/{id}/issues - List issues (filterable by status/priority)
- POST /projects/{id}/issues - Create issue
- GET /issues/{id} - Get single issue
- PATCH /issues/{id} - Update issue (partial)
- DELETE /issues/{id} - Delete issue (permanent)

Note: Only project owners can manage issues
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.issue import IssueStatus, IssuePriority
from app.auth_deps import auth

from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse
from app.services.issue import issue_service


# ═══════════════════════════════════════════════
# Router Configuration
# ═══════════════════════════════════════════════

# No prefix - routes use /projects/{id}/issues and /issues/{id} paths
router = APIRouter(tags=["Issues"])


# ═══════════════════════════════════════════════
# List Project Issues (with Filters)
# ═══════════════════════════════════════════════

@router.get("/projects/{project_id}/issues", response_model=List[IssueResponse])
def get_project_issues(
    project_id: int,                                      # From URL path: /projects/5/issues
    status: Optional[IssueStatus] = Query(None),          # Optional filter: ?status=Open (FastAPI validates against IssueStatus enum)
    priority: Optional[IssuePriority] = Query(None),      # Optional filter: ?priority=High (FastAPI validates against IssuePriority enum)
    database_session: Session = Depends(get_db),          # Database session (injected by FastAPI)
    current_user: User = Depends(auth)                     # Logged-in user (extracted from JWT, injected by FastAPI)
):
    """
    Get all issues in a project, optionally filtered by status/priority.
    
    Flow: Verify user owns project → Query issues WHERE project_id=X → Apply filters → Return list
    
    Examples:
        GET /projects/5/issues                         → All issues
        GET /projects/5/issues?status=Open&priority=High → Filtered
    
    Returns: List of IssueResponse objects (id, title, status, priority, project_id, created_by, created_at)
    Errors: 403 (not owner), 404 (project not found)
    """
    return issue_service.get_project_issues(database_session, project_id, current_user, status, priority)



# ═══════════════════════════════════════════════
# Create Issue
# ═══════════════════════════════════════════════

@router.post("/projects/{project_id}/issues", 
    response_model=IssueResponse,         # Validates response matches IssueResponse schema
    status_code=status.HTTP_201_CREATED  # 201 = resource created successfully
)
def create_issue(
    project_id: int,                                   # From URL path
    issue_data: IssueCreate,                           # From request body (FastAPI validates JSON against IssueCreate schema)
    database_session: Session = Depends(get_db),
    current_user: User = Depends(auth)
):
    """
    Create new issue in a project.
    
    Flow: Validate JSON → Verify user owns project → INSERT INTO issues → Return with auto-generated ID
    
    Request: {"title": "Fix bug", "description": "...", "status": "Open", "priority": "High"}
             (only title required, others optional)
    
    Response: Same fields + id (auto-generated), project_id, created_by, created_at (auto-set)
    Errors: 403 (not owner), 404 (project not found), 422 (invalid data)
    """
    return issue_service.create_issue(database_session, project_id, issue_data, current_user)




# ═══════════════════════════════════════════════
# Get Issue Details
# ═══════════════════════════════════════════════

@router.get("/issues/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: int,                                     # From URL path: /issues/10
    database_session: Session = Depends(get_db),
    current_user: User = Depends(auth)
):
    """
    Get single issue by ID.
    
    Flow: SELECT FROM issues WHERE id=X → Verify user owns parent project → Return issue
    
    Returns: IssueResponse with all fields (id, title, description, status, priority, project_id, created_by, created_at, updated_at)
    Errors: 403 (not owner of project), 404 (issue not found)
    """
    return issue_service.get_issue(database_session, issue_id, current_user)



# ═══════════════════════════════════════════════
# Update Issue
# ═══════════════════════════════════════════════

@router.patch("/issues/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,                                     # From URL path
    issue_data: IssueUpdate,                           # From request body (FastAPI validates, all fields optional - partial update)
    database_session: Session = Depends(get_db),
    current_user: User = Depends(auth)
):
    """
    Update issue (partial - only send fields you want to change).
    
    Flow: Validate JSON → Fetch issue → Verify user owns project → UPDATE only provided fields → Set updated_at
    
    Request: {"status": "Closed"} or {"status": "In Progress", "priority": "Low"} etc.
    Response: Full updated issue with new updated_at timestamp
    Errors: 403 (not owner), 404 (not found), 422 (invalid values)
    """
    return issue_service.update_issue(database_session, issue_id, issue_data, current_user)



# ═══════════════════════════════════════════════
# Delete Issue
# ═══════════════════════════════════════════════

@router.delete("/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(
    issue_id: int,                                     # From URL path
    database_session: Session = Depends(get_db),
    current_user: User = Depends(auth)
):
    """
    Delete issue permanently (cannot be undone).
    
    Flow: Fetch issue → Verify user owns project → DELETE FROM issues WHERE id=X
    
    Returns: Empty response with 204 status (success, no content)
    Errors: 403 (not owner), 404 (not found)
    Note: Consider setting status="Closed" instead to preserve history
    """
    issue_service.delete_issue(database_session, issue_id, current_user)
    return None  # FastAPI converts to 204 No Content