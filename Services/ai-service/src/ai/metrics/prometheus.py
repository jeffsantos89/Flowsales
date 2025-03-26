from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client.exposition import start_http_server
from functools import wraps
import time
import logging
from typing import Optional, Callable
import threading

logger = logging.getLogger(__name__)

class PrometheusMetrics:
    """
    A robust Prometheus metrics handler for monitoring AI service performance and operations.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Request metrics
            self.request_counter = Counter(
                'ai_service_requests_total',
                'Total number of AI service requests',
                ['endpoint', 'status']
            )

            # Latency metrics
            self.request_latency = Histogram(
                'ai_service_request_duration_seconds',
                'Request duration in seconds',
                ['endpoint'],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            )

            # Resource utilization
            self.memory_usage = Gauge(
                'ai_service_memory_usage_bytes',
                'Current memory usage of the AI service'
            )

            # Model information
            self.model_info = Info(
                'ai_service_model',
                'Information about the AI model being used'
            )

            # Error metrics
            self.error_counter = Counter(
                'ai_service_errors_total',
                'Total number of errors',
                ['error_type']
            )

            # Processing queue size
            self.queue_size = Gauge(
                'ai_service_queue_size',
                'Current size of the processing queue'
            )

            self.initialized = True

    def start_metrics_server(self, port: int = 8000) -> None:
        """Start the Prometheus metrics server on the specified port."""
        try:
            start_http_server(port)
            logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {str(e)}")
            raise

    def track_request_latency(self, endpoint: str) -> Callable:
        """Decorator to track request latency for specific endpoints."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    self.request_counter.labels(endpoint=endpoint, status="success").inc()
                    return result
                except Exception as e:
                    self.request_counter.labels(endpoint=endpoint, status="error").inc()
                    self.error_counter.labels(error_type=type(e).__name__).inc()
                    raise
                finally:
                    self.request_latency.labels(endpoint=endpoint).observe(
                        time.time() - start_time
                    )
            return wrapper
        return decorator

    def update_model_info(self, model_name: str, version: str, parameters: Optional[dict] = None) -> None:
        """Update the AI model information metrics."""
        info = {
            "model_name": model_name,
            "version": version,
        }
        if parameters:
            info.update(parameters)
        self.model_info.info(info)

    def set_queue_size(self, size: int) -> None:
        """Update the current processing queue size."""
        self.queue_size.set(size)

    def record_error(self, error_type: str) -> None:
        """Record an error occurrence."""
        self.error_counter.labels(error_type=error_type).inc()

    def update_memory_usage(self, usage_bytes: float) -> None:
        """Update the current memory usage metric."""
        self.memory_usage.set(usage_bytes)

# Usage example:
# metrics = PrometheusMetrics()
# metrics.start_metrics_server()
# 
# @metrics.track_request_latency("predict")
# async def predict():
#     # Your prediction logic here
#     pass