import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.util.types import Attributes

logger = logging.getLogger(__name__)

class TelemetryConfig:
    def __init__(
        self,
        service_name: str,
        endpoint: str = "http://localhost:4317",
        environment: str = "development",
        sample_rate: float = 1.0,
        additional_attributes: Optional[Dict[str, Any]] = None
    ):
        self.service_name = service_name
        self.endpoint = endpoint
        self.environment = environment
        self.sample_rate = sample_rate
        self.additional_attributes = additional_attributes or {}

@lru_cache(maxsize=1)
def create_resource(config: TelemetryConfig) -> Resource:
    """Create telemetry resource with service information."""
    attributes = {
        SERVICE_NAME: config.service_name,
        "deployment.environment": config.environment,
        **config.additional_attributes
    }
    return Resource.create(attributes)

def setup_telemetry(
    app,
    config: TelemetryConfig,
    *,
    enable_fastapi_support: bool = True
) -> None:
    """
    Configure OpenTelemetry with advanced settings for production use.
    
    Args:
        app: FastAPI application instance
        config: TelemetryConfig instance containing telemetry settings
        enable_fastapi_support: Whether to enable FastAPI instrumentation
    
    Raises:
        Exception: If telemetry setup fails
    """
    try:
        # Configure sampler for production traffic management
        sampler = TraceIdRatioBased(config.sample_rate)
        
        # Initialize TracerProvider with resource and sampler
        tracer_provider = TracerProvider(
            resource=create_resource(config),
            sampler=sampler
        )
        
        # Configure OTLP exporter with error handling
        otlp_exporter = OTLPSpanExporter(
            endpoint=config.endpoint,
            insecure=config.environment == "development"
        )
        
        # Configure batch processor with production settings
        span_processor = BatchSpanProcessor(
            otlp_exporter,
            max_export_batch_size=512,
            max_queue_size=2048,
            schedule_delay_millis=5000,
            export_timeout_millis=30000
        )
        
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
        
        if enable_fastapi_support:
            FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=tracer_provider,
                excluded_urls="health,metrics",  # Common endpoints to exclude
                record_exception_stacks=True
            )
        
        logger.info(
            "Telemetry configured successfully",
            extra={
                "service": config.service_name,
                "environment": config.environment,
                "endpoint": config.endpoint
            }
        )
    
    except Exception as e:
        logger.error(f"Failed to configure telemetry: {str(e)}")
        raise

# Usage example:
# config = TelemetryConfig(
#     service_name="ai-service",
#     endpoint="http://otel-collector:4317",
#     environment="production",
#     sample_rate=0.1,
#     additional_attributes={"version": "1.0.0"}
# )
# setup_telemetry(app, config)