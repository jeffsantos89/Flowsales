from typing import Optional
from http import HTTPStatus

class AIServiceException(Exception):
    """Base exception class for AI Service related errors."""
    def __init__(self, message: str, status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class ModelNotFoundError(AIServiceException):
    """Raised when an AI model is not found."""
    def __init__(self, model_id: str, message: Optional[str] = None):
        super().__init__(
            message or f"AI Model with ID '{model_id}' not found",
            status_code=HTTPStatus.NOT_FOUND,
            error_code="MODEL_NOT_FOUND"
        )

class InvalidModelInputError(AIServiceException):
    """Raised when input data for the AI model is invalid."""
    def __init__(self, message: str):
        super().__init__(
            message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code="INVALID_MODEL_INPUT"
        )

class ModelInferenceError(AIServiceException):
    """Raised when there's an error during model inference."""
    def __init__(self, message: str):
        super().__init__(
            message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code="MODEL_INFERENCE_ERROR"
        )

class AuthenticationError(AIServiceException):
    """Raised when there's an authentication error."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )

class RateLimitExceededError(AIServiceException):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED"
        )

class ResourceExhaustedError(AIServiceException):
    """Raised when service resources are exhausted."""
    def __init__(self, resource_type: str):
        super().__init__(
            f"Resource exhausted: {resource_type}",
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            error_code="RESOURCE_EXHAUSTED"
        )

class InvalidConfigurationError(AIServiceException):
    """Raised when service configuration is invalid."""
    def __init__(self, message: str):
        super().__init__(
            message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code="INVALID_CONFIGURATION"
        )