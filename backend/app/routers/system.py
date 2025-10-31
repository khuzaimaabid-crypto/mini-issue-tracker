"""
System Router - Infrastructure & Monitoring Endpoints
=====================================================

This module contains system-level endpoints that are not part of the business logic.
These endpoints are used by infrastructure, monitoring tools, and provide API metadata.

Endpoints:
- GET / - API information and version
- GET /health - Health check for monitoring/load balancers

Note: These endpoints don't require authentication and should be lightweight.
"""

from fastapi import APIRouter
from app.config import settings


# ═══════════════════════════════════════════════
# Router Configuration
# ═══════════════════════════════════════════════

router = APIRouter(tags=["System"])


# ═══════════════════════════════════════════════
# Root Endpoint - API Information
# ═══════════════════════════════════════════════

@router.get("/")
def root():
    """
    Root endpoint - provides basic API information.
    
    Used for:
    - Quick verification that API is running
    - Discovering documentation URL
    - Checking API version
    
    Returns:
        dict: API metadata including version and docs link
    
    Example response:
        {
            "message": "Mini Issue Tracker API",
            "version": "1.0.0",
            "docs": "/docs"
        }
    """
    return {
        "message": "Mini Issue Tracker API",
        "version": settings.VERSION,
        "docs": "/docs"  # Interactive API documentation (Swagger UI)
    }


# ═══════════════════════════════════════════════
# Health Check Endpoint
# ═══════════════════════════════════════════════

@router.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Used by:
    - Docker health checks (docker-compose.yml)
    - Kubernetes liveness/readiness probes
    - Monitoring tools (Prometheus, Datadog, etc.)
    - Load balancers to check if instance is healthy
    
    Returns:
        dict: Simple status indicator
    
    Example response:
        {"status": "healthy"}
    
    Note: In production, consider checking database connectivity:
          try:
              db.execute("SELECT 1")
              return {"status": "healthy"}
          except:
              return {"status": "unhealthy"}, 503
    """
    return {"status": "healthy"}
