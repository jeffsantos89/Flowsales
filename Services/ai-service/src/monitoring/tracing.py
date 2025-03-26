import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.util.types import Attributes

logger = logging.getLogger(__name__)

class TracingConfig:
    def __init__(
        self,
        service_name: str,
        collector_endpoint: str = "http://otel-collector:4317",
        environment: str = "production",
        enable_console_export: bool = False
    ):
        self.service_name = service_name
        self.collector_endpoint = collector_endpoint
        self.environment = environment
        self.enable_console_export = enable_console_export

class TracingManager:
    def __init__(self, config: TracingConfig):
        self.config = config
        self.tracer_provider = None
        self.tracer = None
        self.setup_tracing()

    def setup_tracing(self) -> None:
        try:
            resource = Resource.create({
                "service.name": self.config.service_name,
                "environment": self.config.environment,
            })

            self.tracer_provider = TracerProvider(resource=resource)
            
            # Configure OTLP exporter
            otlp_exporter = OTLPSpanExporter(endpoint=self.config.collector_endpoint)
            self.tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

            # Optional console exporter for debugging
            if self.config.enable_console_export:
                console_exporter = ConsoleSpanExporter()
                self.tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))

            trace.set_tracer_provider(self.tracer_provider)
            self.tracer = trace.get_tracer(__name__)

        except Exception as e:
            logger.error(f"Failed to initialize tracing: {str(e)}")
            raise

    @contextmanager
    def create_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: Optional[trace.SpanKind] = trace.SpanKind.INTERNAL
    ):
        """
        Context manager for creating and managing spans.
        """
        try:
            span_attributes: Attributes = attributes or {}
            with self.tracer.start_as_current_span(
                name,
                attributes=span_attributes,
                kind=kind
            ) as span:
                yield span
        except Exception as e:
            if span and span.is_recording():
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise

    def inject_context_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Injects trace context into headers for distributed tracing.
        """
        propagator = TraceContextTextMapPropagator()
        propagator.inject(headers)
        return headers

# Usage example:
# config = TracingConfig(service_name="my-service", environment="production")
# tracing = TracingManager(config)
# 
# with tracing.create_span("operation_name", attributes={"key": "value"}) as span:
#     # Your code here
#     span.add_event("something_happened")
