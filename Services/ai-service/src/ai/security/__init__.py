from typing import List, Any, Optional
from abc import ABC, abstractmethod
import re

"""
Core infrastructure module for Flowsale AI service.
Provides exception handling, input validation, and core utilities.

This module serves as the central hub for all shared functionality across the AI service,
including exception handling, input validation, and common utilities.
"""


# Base Exception Class
class AIServiceException(Exception):
    """Base exception class for all AI service related errors."""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

# Specific Exception Classes
class ModelNotFoundError(AIServiceException):
    """Raised when requested AI model is not found."""
    pass

class InvalidModelInputError(AIServiceException):
    """Raised when model input validation fails."""
    pass

class ModelInferenceError(AIServiceException):
    """Raised when model inference encounters an error."""
    pass

class AuthenticationError(AIServiceException):
    """Raised for authentication related errors."""
    pass

class RateLimitExceededError(AIServiceException):
    """Raised when API rate limits are exceeded."""
    pass

class ResourceExhaustedError(AIServiceException):
    """Raised when system resources are exhausted."""
    pass

class InvalidConfigurationError(AIServiceException):
    """Raised for configuration related errors."""
    pass

# Input Validation
class InputValidator(ABC):
    """Abstract base class for input validation."""
    
    @abstractmethod
    def validate(self, input_data: Any) -> bool:
        """Validate input data."""
        pass

class EmailValidator(InputValidator):
    """Email validation implementation."""
    
    def validate(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

def validate_input(input_data: Any, validator: InputValidator) -> bool:
    """Generic input validation function."""
    try:
        return validator.validate(input_data)
    except Exception as e:
        raise ValidationError(f"Validation failed: {str(e)}")

class ValidationError(AIServiceException):
    """Raised when input validation fails."""
    pass

# Module exports
__all__: List[str] = [
    # Exceptions
    "AIServiceException",
    "ModelNotFoundError",
    "InvalidModelInputError",
    "ModelInferenceError",
    "AuthenticationError",
    "RateLimitExceededError",
    "ResourceExhaustedError",
    "InvalidConfigurationError",
    "ValidationError",
    # Validation
    "InputValidator",
    "EmailValidator",
    "validate_input",
]
