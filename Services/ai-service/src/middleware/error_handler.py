import logging
from typing import Any, Dict, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import traceback
import sys
import uuid
from fastapi import FastAPI
from middleware.error_handler import ErrorHandler, CustomException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomException(Exception):
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class ErrorHandler(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        error_id = str(uuid.uuid4())
        try:
            return await call_next(request)

        except CustomException as ce:
            return self._handle_custom_exception(ce, error_id)

        except ValueError as ve:
            return self._handle_validation_error(ve, error_id)

        except Exception as e:
            return self._handle_internal_error(e, error_id)

    def _handle_custom_exception(self, exc: CustomException, error_id: str) -> JSONResponse:
        self._log_error(exc, error_id)
        return JSONResponse(
            status_code=exc.status_code,
            content=self._build_error_response(
                message=exc.message,
                error_code=exc.error_code,
                error_id=error_id
            )
        )

    def _handle_validation_error(self, exc: ValueError, error_id: str) -> JSONResponse:
        self._log_error(exc, error_id)
        return JSONResponse(
            status_code=400,
            content=self._build_error_response(
                message="Validation error",
                error_code="VALIDATION_ERROR",
                error_id=error_id,
                details=str(exc)
            )
        )

    def _handle_internal_error(self, exc: Exception, error_id: str) -> JSONResponse:
        self._log_error(exc, error_id)
        return JSONResponse(
            status_code=500,
            content=self._build_error_response(
                message="Internal server error",
                error_code="INTERNAL_ERROR",
                error_id=error_id
            )
        )

    def _log_error(self, exc: Exception, error_id: str) -> None:
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_id': error_id,
            'error_type': exc.__class__.__name__,
            'error_message': str(exc),
            'stacktrace': traceback.format_exception(*sys.exc_info())
        }
        logger.error(f"Error occurred: {error_data}")

    def _build_error_response(
        self,
        message: str,
        error_code: Optional[str],
        error_id: str,
        details: Any = None
    ) -> Dict[str, Any]:
        response = {
            'success': False,
            'error': {
                'message': message,
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        if error_code:
            response['error']['code'] = error_code
            
        if details:
            response['error']['details'] = details

        return response

# Usage example:
"""

app = FastAPI()
app.add_middleware(ErrorHandler)

@app.get("/test-error")
async def test_error():
    raise CustomException(
        message="Something went wrong",
        status_code=400,
        error_code="CUSTOM_ERROR"
    )
"""