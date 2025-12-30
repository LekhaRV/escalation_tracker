"""
Tarento AI Complaint Tracking System - Custom Exceptions
"""

from typing import Optional, Dict, Any


class AppError(Exception):
    """Base application error"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """Validation error (400)"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class AuthenticationError(AppError):
    """Authentication error (401)"""
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message, status_code=401)


class AuthorizationError(AppError):
    """Authorization error (403)"""
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message, status_code=403)


class NotFoundError(AppError):
    """Resource not found error (404)"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(AppError):
    """Conflict error (409)"""
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class DatabaseError(AppError):
    """Database error (500)"""
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, status_code=500)


class ExternalServiceError(AppError):
    """External service error (503)"""
    def __init__(self, message: str = "External service unavailable"):
        super().__init__(message, status_code=503)


class RateLimitError(AppError):
    """Rate limit exceeded error (429)"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)
