"""
Issue Schemas
=============

Pydantic models for issue data validation (create, update, filter, responses).

Key features:
- Reuses IssueStatus and IssuePriority enums from models (type safety)
- Provides sensible defaults (OPEN status, MEDIUM priority)
- All fields optional in update for partial updates
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.issue import IssueStatus, IssuePriority  # Reuse enums from database model


class IssueBase(BaseModel):
    """
    Base issue fields shared across schemas.
    
    Contains: Core issue fields with default values
    Defaults: New issues are OPEN with MEDIUM priority
    """
    title: str = Field(..., min_length=1, max_length=300)  # Issue title (required)
    description: Optional[str] = None                      # Optional detailed description
    status: IssueStatus = IssueStatus.OPEN                 # Default: OPEN (can be IN_PROGRESS, CLOSED)
    priority: IssuePriority = IssuePriority.MEDIUM         # Default: MEDIUM (can be LOW, HIGH)


class IssueCreate(IssueBase):
    """
    Schema for issue creation request.
    
    Used by: POST /projects/{id}/issues
    Inherits: All fields from IssueBase (title, description, status, priority)
    """
    pass  # No additional fields needed


class IssueUpdate(BaseModel):
    """
    Schema for issue update request.
    
    Used by: PATCH /issues/{id}
    Note: All fields optional to allow partial updates (e.g., change only status)
    """
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[IssueStatus] = None      # Update status: OPEN → IN_PROGRESS → CLOSED
    priority: Optional[IssuePriority] = None  # Update priority: LOW ↔ MEDIUM ↔ HIGH


class IssueResponse(IssueBase):
    """
    Schema for issue data in API responses.
    
    Returned by: GET/POST/PATCH /issues endpoints
    Includes: Database-generated fields (id, project_id, created_by, timestamps)
    """
    id: int
    project_id: int   # Which project this issue belongs to
    created_by: int   # User ID who created this issue
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)  # Converts SQLAlchemy model → Pydantic


class IssueFilter(BaseModel):
    """
    Schema for filtering issues in list queries.
    
    Used by: GET /projects/{id}/issues?status=OPEN&priority=HIGH
    Allows: Filtering by status and/or priority (both optional)
    """
    status: Optional[IssueStatus] = None      # Filter by status (e.g., show only OPEN issues)
    priority: Optional[IssuePriority] = None  # Filter by priority (e.g., show only HIGH priority)