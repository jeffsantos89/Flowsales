from enum import Enum
from typing import Any, Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from core.exceptions import BaseApplicationError
from core.logger import logger
import traceback
import uuid


class ResponseStatus(str, Enum):
    ERROR = "error"
    SUCCESS = "success"


class ErrorResponse:
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.correlation_id = correlation_id or str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        response = {
            "status": ResponseStatus.ERROR,
            "error": self.message,
            "correlation_id": self.correlation_id
        }
        
        if self.error_code:
            response["code"] = self.error_code
        
        if self.details:
            response["details"] = self.details
            
        return response


async def get_correlation_id(request: Request) -> str:
    """Extract or generate correlation ID from request headers."""
    return request.headers.get("X-Correlation-ID") or str(uuid.uuid4())


async def log_error(correlation_id: str, error_type: str, message: str, exc_info: bool = False) -> None:
    """Centralized error logging function."""
    log_message = f"[{correlation_id}] {error_type}: {message}"
    if exc_info:
        logger.exception(log_message)
    else:
        logger.error(log_message)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for all API endpoints.
    Handles different types of exceptions and returns appropriate JSON responses.
    """
    correlation_id = await get_correlation_id(request)

    try:
        if isinstance(exc, BaseApplicationError):
            error_response = ErrorResponse(
                status_code=exc.status_code,
                message=exc.message,
                error_code=exc.error_code,
                details=exc.details,
                correlation_id=correlation_id
            )
            await log_error(correlation_id, exc.__class__.__name__, exc.message)
            
        elif isinstance(exc, HTTPException):
            error_response = ErrorResponse(
                status_code=exc.status_code,
                message=exc.detail,
                correlation_id=correlation_id
            )
            await log_error(correlation_id, "HTTPException", exc.detail)
            
        else:
            error_response = ErrorResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal Server Error",
                correlation_id=correlation_id
            )
            await log_error(
                correlation_id,
                "Unhandled Exception",
                str(exc),
                exc_info=True
            )

        return JSONResponse(
            status_code=error_response.status_code,
            content=error_response.to_dict()
        )

    except Exception as e:
        # Fallback error handler
        logger.critical(f"Error in exception handler: {str(e)}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": ResponseStatus.ERROR,
                "error": "Critical error in error handling",
                "correlation_id": correlation_id
            }
        )


"""
Usage in main app:

from fastapi import FastAPI
from core.exception_handler import global_exception_handler

app = FastAPI()
app.add_exception_handler(Exception, global_exception_handler)
"""
