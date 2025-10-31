"""
Master Router - Central Registry of All API Routes
==================================================

This file combines all individual routers into a single api_router.
Import this in main.py to register all routes at once.

Why This File?
- Single source of truth for all API routes
- Easy to add new routers (just add to ROUTERS list)
- Keeps main.py clean and focused
- Follows FastAPI official template pattern
"""

from fastapi import APIRouter
from app.routers import system, auth, projects, issues


# ═══════════════════════════════════════════════
# Master API Router
# ═══════════════════════════════════════════════

api_router = APIRouter()


# ═══════════════════════════════════════════════
# Router Registry
# ═══════════════════════════════════════════════

# List of all router modules to include
# Add new router modules here as you create them
# Note: Order matters - system endpoints (/, /health) should be first
ROUTERS = [
    system,      # System endpoints: /, /health (no auth required)
    auth,        # Authentication: /auth/register, /auth/login
    projects,    # Projects: /projects/*
    issues,      # Issues: /projects/{id}/issues, /issues/{id}
]


# ═══════════════════════════════════════════════
# Include All Routers
# ═══════════════════════════════════════════════

# Each router already has its own prefix and tags defined
# e.g., auth.router has prefix="/auth", tags=["Authentication"]
for router_module in ROUTERS:
    api_router.include_router(router_module.router)
