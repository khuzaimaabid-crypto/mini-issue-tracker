"""
Database Configuration
======================

This module sets up SQLAlchemy for database access. Three main components:

1. DatabaseEngine:
   - Manages the connection pool to PostgreSQL
   - Connection pool = Reusable set of database connections (more efficient than creating new ones)
   - Think: A pool of phone lines to the database, reused across requests

2. SessionMaker:
   - Creates database sessions when called
   - Session = Workspace for your database operations (load objects, make changes, commit/rollback)
   - Each API request gets its own isolated session
   - NOT the same as a connection - sessions borrow connections from the pool when needed

3. ModelBase:
   - Parent class that all models inherit from (User, Project, Issue)
   - SQLAlchemy inspects classes inheriting from ModelBase to auto-generate database tables
   - When you write: class User(ModelBase), SQLAlchemy creates the 'users' table

4. get_db():
   - FastAPI dependency that provides a session to route handlers
   - Automatically creates session → passes to route → closes after request completes
   - Uses 'yield' to ensure cleanup happens even if errors occur

Flow: Request comes in → FastAPI calls get_db() → Creates session → 
      Route uses session → Request ends → Session closes → Connection returns to pool
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# ═══════════════════════════════════════════════
# Database Engine - Connection Pool Manager
# ═══════════════════════════════════════════════

# Connection pool that manages database connections to PostgreSQL
# SQLAlchemy calls this 'engine' (standard naming convention in their docs)
DatabaseEngine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # Test connection health before using (handles stale connections)
    pool_size=10,            # Maintain 10 persistent connections in the pool
    max_overflow=20,         # Allow 20 additional connections during traffic spikes (total: 30)
    echo=settings.DEBUG      # Log all SQL queries to console when DEBUG=True
)

# ═══════════════════════════════════════════════
# Session Factory - Creates Database Sessions
# ═══════════════════════════════════════════════

# Creates new database sessions - each session is an isolated workspace for database operations
# Call this to get a new session: session = SessionMaker()
SessionMaker = sessionmaker(
    autocommit=False,        # Require explicit db.commit() to save changes (prevents accidental writes)
    autoflush=False,         # Don't auto-sync Python objects to DB before queries (better performance)
    bind=DatabaseEngine      # Connect this session maker to our database engine above
)

# ═══════════════════════════════════════════════
# Model Base Class - Parent for All ORM Models
# ═══════════════════════════════════════════════

# Parent class that all models inherit from (User, Project, Issue)
# When you write: class User(ModelBase), SQLAlchemy knows to create a database table
ModelBase = declarative_base()


# ═══════════════════════════════════════════════
# FastAPI Dependency - Session Provider
# ═══════════════════════════════════════════════

def get_db():
    """
    Database session provider for FastAPI dependency injection.
    
    Used in routes like: def my_route(db: Session = Depends(get_db))
    
    FastAPI automatically:
    1. Calls this function before route handler executes
    2. Passes the yielded session to the route as 'db' parameter
    3. Runs the finally block after route completes (closes session)
    
    The session is isolated per request - changes in one request don't affect others
    until committed. If an exception occurs, changes are automatically rolled back.
    
    Example usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()  # Uses the session provided by this function
            return users
            # Session automatically closes after this function completes
    """
    session = SessionMaker()  # Create new session for this request
    try:
        yield session  # Provide session to route handler (pauses here while route executes)
    finally:
        session.close()  # Always close session, returning connection to pool