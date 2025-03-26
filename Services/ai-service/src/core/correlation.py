import logging
from typing import Optional, Callable
from starlette.middleware.base import RequestResponseEndpoint, BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from uuid import uuid4

class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle correlation IDs for request tracing."""

    def __init__(
        self,
        app,
        header_name: str = "X-Correlation-ID",
        validate_uuid: bool = True,
        logger: Optional[logging.Logger] = None,
        generator_func: Optional[Callable[[], str]] = None
    ):
        super().__init__(app)
        self.header_name = header_name
        self.validate_uuid = validate_uuid
        self.logger = logger or logging.getLogger(__name__)
        self.generator_func = generator_func or (lambda: str(uuid4()))

    def is_valid_uuid(self, uuid_str: str) -> bool:
        """Validate if the string is a valid UUID."""
        try:
            uuid4(uuid_str)
            return True
        except ValueError:
            return False

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get or generate correlation ID
        correlation_id = request.headers.get(self.header_name)

        if not correlation_id:
            correlation_id = self.generator_func()
        elif self.validate_uuid and not self.is_valid_uuid(correlation_id):
            self.logger.warning(f"Invalid correlation ID received: {correlation_id}")
            correlation_id = self.generator_func()

        # Add correlation ID to request state
        request.state.correlation_id = correlation_id

        try:
            # Add correlation ID to logger context
            ctx_logger = self.logger.bind(correlation_id=correlation_id)
            ctx_logger.debug(f"Processing request with correlation ID: {correlation_id}")

            # Process the request
            response: Response = await call_next(request)

            # Add correlation ID to response headers
            response.headers[self.header_name] = correlation_id
            return response

        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}", extra={"correlation_id": correlation_id})
            raise
