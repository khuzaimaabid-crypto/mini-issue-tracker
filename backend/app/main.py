"""
Application Entry Point
=======================

This module initializes and configures the FastAPI application. Key components:

1. FastAPI Application Instance:
   - Central object that handles all HTTP requests
   - Automatically generates OpenAPI/Swagger documentation at /docs
   - Manages routing, middleware, and dependency injection

2. CORS Middleware:
   - Allows frontend (running on different port/domain) to make requests to this API
   - Without CORS, browsers block cross-origin requests for security
   - Example: Frontend at localhost:5173 can call API at localhost:8000

3. Router Registration:
   - Routers group related endpoints (auth, projects, issues)
   - Each router is defined in separate files under app/routers/
   - Keeps code organized and maintainable

4. Database Schema Management:
   - Uses Alembic for migrations (NOT auto-create from models)
   - Alembic tracks schema changes, enables rollbacks, and team synchronization
   - See "Database Migrations" section below for workflow

Important: This file does NOT create database tables automatically.
Use Alembic migrations instead (see workflow below).
"""

from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import ModelBase, DatabaseEngine
from app.routers.routes import api_router  # Master router that includes all routes

ModelBase.metadata.create_all(bind=DatabaseEngine)

# ═══════════════════════════════════════════════
# Database Migrations - Use Alembic, Not Auto-Create
# ═══════════════════════════════════════════════
#
# ❌ BAD PRACTICE (To be removed):
#    ModelBase.metadata.create_all(bind=DatabaseEngine)
#    - Cannot modify existing tables (add/remove columns)
#    - No migration history or rollback capability
#    - Causes production data loss
#
# ✅ CORRECT APPROACH - Alembic Migration Workflow:
#
#    1. Create migration after model changes:
#       $ alembic revision --autogenerate -m "Add user email column"
#       (Alembic detects changes in app/models/*.py and generates migration)
#
#    2. Review generated migration:
#       $ cat alembic/versions/xxxxx_add_user_email_column.py
#       (Always review! Auto-generate isn't perfect)
#
#    3. Apply migration to database:
#       $ alembic upgrade head
#       (Safely updates schema without losing data)
#
#    4. Rollback if needed:
#       $ alembic downgrade -1
#       (Undo last migration)
#
#    5. Check current version:
#       $ alembic current
#
# Note: First-time setup requires running migrations to create initial tables.
# See README.md for setup instructions.


# ═══════════════════════════════════════════════
# FastAPI Application Instance
# ═══════════════════════════════════════════════

# Create the main FastAPI application
# This object handles all incoming HTTP requests and routes them to appropriate handlers
app = FastAPI(
    title=settings.APP_NAME,              # Shows in API documentation at /docs
    version=settings.VERSION,              # API version for client compatibility tracking
    description="Mini Issue Tracker API with JWT Authentication"  # Appears in /docs homepage
)


# ═══════════════════════════════════════════════
# CORS Middleware - Enable Cross-Origin Requests
# ═══════════════════════════════════════════════

# CORS (Cross-Origin Resource Sharing) allows frontend to call this API
# Without this, browsers block requests from different origins (ports/domains)
# Example: Frontend at http://localhost:5173 → Backend at http://localhost:8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # List of allowed frontend URLs (from config)
    allow_credentials=True,               # Allow cookies/auth headers in cross-origin requests
    allow_methods=["*"],                  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],                  # Allow all headers (Content-Type, Authorization, etc.)
)

# ═══════════════════════════════════════════════
# Debugging Configuration - Enable debugpy if LOG_LEVEL=debug
# ═══════════════════════════════════════════════
# Conditionally enable debugging based on LOG_LEVEL

log_level = os.getenv("LOG_LEVEL", "debug").lower()
if log_level == "debug":
    import debugpy
    # listen for debugpy
   #  debugpy.listen(("0.0.0.0", 5678))
    print("Debug mode enabled. Waiting for debugger to attach...")


# ═══════════════════════════════════════════════
# Router Registration - All Endpoints
# ═══════════════════════════════════════════════

# Master API router includes all routes:
# - System endpoints (/, /health)
# - Business logic endpoints (auth, projects, issues)
# Individual routers are configured in app/routers/routes.py
# This keeps main.py minimal and focused on application setup
app.include_router(api_router)