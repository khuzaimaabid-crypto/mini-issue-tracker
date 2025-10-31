"""
Custom HTTP Exceptions - Standardized error responses

Each exception class represents a specific HTTP error status.
Instead of manually creating HTTPException everywhere, use these custom classes.

Usage: raise NotFoundException(detail="User not found")
Result: FastAPI returns {"detail": "User not found"} with status 404
"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """404 Not Found - Resource doesn't exist (user, project, issue not found)"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(HTTPException):
    """401 Unauthorized - Invalid credentials (wrong password, invalid/expired token)"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}  # Tells client to send Bearer token
        )


class ForbiddenException(HTTPException):
    """403 Forbidden - Valid credentials but no permission (accessing someone else's project)"""
    def __init__(self, detail: str = "You don't have permission to access this resource"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(HTTPException):
    """400 Bad Request - Invalid input data (malformed request, validation errors)"""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(HTTPException):
    """409 Conflict - Resource already exists (duplicate email, name collision)"""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)