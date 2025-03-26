# src/observability/observability_orchestrator.py

from typing import Any, Callable, Dict
from dataclasses import dataclass
from time import time
from fastapi import Request, Response
import traceback
import logging
from contextlib import contextmanager

from metrics import metrics
from tracing import tracing
from alerting import send_alert, alert_high_latency, alert_error_rate
from log_config import structured_log

@dataclass
class RequestContext:
    method: str
    endpoint: str
    correlation_id: str
    start_time: float
    
    @property
    def latency(self) -> float:
        return time() - self.start_time

class ObservabilityOrchestrator:
    def __init__(
        self,
        latency_threshold: float = 1.0,
        logger: logging.Logger = None
    ):
        self.latency_threshold = latency_threshold
        self.logger = logger or logging.getLogger(__name__)

    def _create_request_context(self, request: Request) -> RequestContext:
        return RequestContext(
            method=request.method,
            endpoint=request.url.path,
            correlation_id=request.headers.get("x-correlation-id", "n/a"),
            start_time=time()
        )

    def _track_metrics(self, ctx: RequestContext, status_code: int) -> None:
        metrics.track_request(
            ctx.method,
            ctx.endpoint,
            ctx.latency,
            status_code
        )

    def _log_request(
        self,
        ctx: RequestContext,
        level: str,
        message: str,
        status: int = None,
        error: Exception = None
    ) -> None:
        extra: Dict[str, Any] = {
            "duration": f"{ctx.latency:.3f}s",
            "method": ctx.method,
            "path": ctx.endpoint
        }

        if status:
            extra["status"] = status
        if error:
            extra.update({
                "exception": str(error),
                "traceback": traceback.format_exc()
            })

        structured_log(
            level=level,
            message=message,
            correlation_id=ctx.correlation_id,
            extra=extra
        )

    @contextmanager
    def _request_tracing(self, ctx: RequestContext):
        with tracing.create_span(
            ctx.endpoint,
            attributes={
                "method": ctx.method,
                "correlation_id": ctx.correlation_id,
                "path": ctx.endpoint
            }
        ):
            yield

    def _handle_alerts(
        self,
        ctx: RequestContext,
        error: Exception = None
    ) -> None:
        if ctx.latency > self.latency_threshold:
            alert_high_latency(ctx.endpoint, ctx.latency)

        if error:
            alert_error_rate(ctx.endpoint)
            send_alert(
                message="Erro crítico detectado",
                level="error",
                context={
                    "endpoint": ctx.endpoint,
                    "error": str(error)
                }
            )

    async def monitor_request(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Middleware for comprehensive request monitoring including logging,
        tracing, metrics, and alerts.
        """
        ctx = self._create_request_context(request)

        with self._request_tracing(ctx):
            try:
                response = await call_next(request)
                
                self._track_metrics(ctx, response.status_code)
                self._log_request(
                    ctx,
                    level="info",
                    message="Request completed successfully",
                    status=response.status_code
                )
                self._handle_alerts(ctx)

                return response

            except Exception as e:
                self._track_metrics(ctx, 500)
                self._log_request(
                    ctx,
                    level="error",
                    message="Internal request error",
                    error=e
                )
                self._handle_alerts(ctx, error=e)

                raise  # Re-raise for FastAPI's error handling
