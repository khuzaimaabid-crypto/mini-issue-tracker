"""
Project Schemas
===============

Pydantic models for project data validation (create, update, responses).

Schema pattern:
- Base: Common fields shared across operations
- Create: Fields required for creation (inherits Base)
- Update: All fields optional for partial updates
- Response: Fields returned in API responses
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ProjectBase(BaseModel):
    """
    Base project fields shared across schemas.
    
    Contains: Fields that appear in both create and response operations
    """
    name: str = Field(..., min_length=1, max_length=200)  # Project name (required)
    description: Optional[str] = None                     # Optional project description


class ProjectCreate(ProjectBase):
    """
    Schema for project creation request.
    
    Used by: POST /projects
    Inherits: All fields from ProjectBase (name, description)
    """
    pass  # No additional fields needed


class ProjectUpdate(BaseModel):
    """
    Schema for project update request.
    
    Used by: PATCH /projects/{id}
    Note: All fields optional to allow partial updates (update only name, or only description)
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    """
    Schema for project data in API responses.
    
    Returned by: GET/POST/PATCH /projects endpoints
    Includes: Database-generated fields (id, timestamps, created_by)
    """
    id: int
    created_by: int              # User ID who created this project
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)  # Converts SQLAlchemy model → Pydantic


class ProjectWithIssueCount(ProjectResponse):
    """
    Extended project response with issue count.
    
    Used by: GET /projects (list endpoint)
    Adds: Aggregated count of issues in this project
    """
    issue_count: int = 0  # Number of issues in this project (default 0 if none)