"""
Issue Model - Database table definition for tasks/bugs

SQLAlchemy ORM model that defines the "issues" table structure.
Alembic reads this to generate CREATE TABLE / ALTER TABLE SQL.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship  # Define relationships between tables
from sqlalchemy.sql import func  # SQL functions like NOW()
from app.database import ModelBase  # Base class all models inherit from
import enum  # Python's enum for creating fixed choices

# Multiple Inheritance(str and enum are parent classes here to create string-based enums)
class IssueStatus(str, enum.Enum):
    """Valid status values: Open, In Progress, Closed"""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


class IssuePriority(str, enum.Enum):
    """Valid priority values: Low, Medium, High"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


# ═══════════════════════════════════════════════
# Issue Model - Maps to "issues" Table
# ═══════════════════════════════════════════════

# ModelBase is parent class here which all classes inherit from
class Issue(ModelBase):
    """Issue model - represents tasks/bugs in projects"""
    
    __tablename__ = "issues"  # PostgreSQL table name
    
    # Columns (database fields)
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN, nullable=False, index=True)
    priority = Column(Enum(IssuePriority), default=IssuePriority.MEDIUM, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # These create attributes to easily navigate between related tables (uses JOINs behind the scenes)
    project = relationship("Project", back_populates="issues")
    # Lets you do: issue.project → returns the Project object this issue belongs to
    
    creator = relationship("User", back_populates="issues")
    # Lets you do: issue.creator → returns the User object who created this issue
    
    def __repr__(self):
        """
        Defines how this object looks when printed (for debugging in terminal/logs).
        Used when debugging: print(issue), logging, Python shell, error messages
        """
        return f"<Issue(id={self.id}, title={self.title}, status={self.status})>"