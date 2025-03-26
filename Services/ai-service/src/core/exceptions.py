from typing import Optional
from http import HTTPStatus

class BaseApplicationError(Exception):
    """Base exception class for all application errors."""
    def __init__(
        self, 
        message: str, 
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class DatabaseError(BaseApplicationError):
    """Exception for database-related errors."""
    def __init__(
        self, 
        message: str = "Database operation failed",
        error_code: Optional[str] = "DB_ERROR",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code=error_code,
            details=details
        )

class ValidationError(BaseApplicationError):
    """Exception for validation errors."""
    def __init__(
        self, 
        message: str = "Validation failed",
        error_code: Optional[str] = "VALIDATION_ERROR",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code=error_code,
            details=details
        )

class NotFoundError(BaseApplicationError):
    """Exception for resource not found errors."""
    def __init__(
        self, 
        message: str = "Resource not found",
        error_code: Optional[str] = "NOT_FOUND",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            error_code=error_code,
            details=details
        )

class UnauthorizedError(BaseApplicationError):
    """Exception for authorization errors."""
    def __init__(
        self, 
        message: str = "Unauthorized access",
        error_code: Optional[str] = "UNAUTHORIZED",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code=error_code,
            details=details
        )

class BadRequestError(BaseApplicationError):
    """Exception for invalid requests."""
    def __init__(
        self, 
        message: str = "Invalid request",
        error_code: Optional[str] = "BAD_REQUEST",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code=error_code,
            details=details
        )