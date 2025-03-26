"""
Core exceptions module for the AI service.
This module provides a comprehensive set of custom exceptions for error handling.
"""

from typing import Union, Optional

# Base Exception
class AIServiceError(Exception):
    """Base exception class for all AI service errors."""
    def __init__(self, message: str, code: Optional[int] = None, details: Optional[dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

# Database Exceptions
class DatabaseError(AIServiceError):
    """Raised when database operations fail."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, code=500, details=details)

# Validation Exceptions
class ValidationError(AIServiceError):
    """Raised when data validation fails."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, code=400, details=details)

# Not Found Exceptions
class NotFoundError(AIServiceError):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, code=404, details=details)

# Authorization Exceptions
class UnauthorizedError(AIServiceError):
    """Raised when authentication fails or is missing."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, code=401, details=details)

# Bad Request Exceptions
class BadRequestError(AIServiceError):
    """Raised when the request is malformed or invalid."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, code=400, details=details)

__all__ = [
    'AIServiceError',
    'DatabaseError',
    'ValidationError',
    'NotFoundError',
    'UnauthorizedError',
    'BadRequestError'
]