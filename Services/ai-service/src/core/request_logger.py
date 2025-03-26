from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from time import time
import traceback
from typing import Optional
from datetime import datetime
from core.logger import logger
import json

class RequestLoggerMiddleware:
    def __init__(self, log_request_body: bool = False, log_headers: bool = True):
        self.log_request_body = log_request_body
        self.log_headers = log_headers

    async def __call__(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time()
        start_dt = datetime.utcnow()
        correlation_id = getattr(request.state, "correlation_id", None)
        error: Optional[Exception] = None
        response: Optional[Response] = None

        # Collect request details
        request_data = {
            "timestamp": start_dt.isoformat(),
            "correlation_id": correlation_id or "none",
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", "unknown")
        }

        if self.log_headers:
            request_data["headers"] = dict(request.headers)

        try:
            if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                try:
                    request_data["body"] = json.loads(body)
                except:
                    request_data["body"] = body.decode()

            # Execute request
            response = await call_next(request)
            
        except Exception as e:
            error = e
            logger.error(f"Request failed: {str(e)}\n{traceback.format_exc()}")
            raise
        
        finally:
            duration = round(time() - start_time, 3)
            status_code = response.status_code if response else 500

            # Collect response details
            log_data = {
                **request_data,
                "duration_seconds": duration,
                "status_code": status_code,
                "success": 200 <= status_code < 400,
            }

            # Log based on status code
            if status_code >= 500:
                logger.error(f"Request failed: {json.dumps(log_data)}")
            elif status_code >= 400:
                logger.warning(f"Request warning: {json.dumps(log_data)}")
            else:
                logger.info(f"Request completed: {json.dumps(log_data)}")

            # Add response headers
            if response:
                response.headers["X-Request-Duration"] = str(duration)
                response.headers["X-Correlation-ID"] = correlation_id or "none"

            return response if response else Response(status_code=500)

async def log_request(request: Request, call_next: RequestResponseEndpoint) -> Response:
    middleware = RequestLoggerMiddleware()
    return await middleware(request, call_next)
