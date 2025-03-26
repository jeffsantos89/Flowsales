from typing import Optional, Dict, Any
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Classe responsável por coletar e gerenciar métricas da aplicação."""
    
    def __init__(self, app_name: str = "app"):
        self.app_name = app_name
        
        # Métricas HTTP
        self.request_count = Counter(
            f"{app_name}_http_requests_total",
            "Total number of HTTP requests received",
            ["method", "endpoint", "status"]
        )
        
        self.response_time = Histogram(
            f"{app_name}_http_response_time_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint", "status"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        # Métricas de sistema
        self.active_requests = Gauge(
            f"{app_name}_active_requests",
            "Number of requests currently being processed",
            ["endpoint"]
        )
        
        self.error_count = Counter(
            f"{app_name}_errors_total",
            "Total number of errors encountered",
            ["method", "endpoint", "error_type"]
        )

    def track_request(
        self,
        method: str,
        endpoint: str,
        status: str,
        duration: float,
        error: Optional[Exception] = None
    ) -> None:
        """
        Registra métricas de uma requisição HTTP.
        
        Args:
            method: Método HTTP
            endpoint: Endpoint da requisição
            status: Status HTTP da resposta
            duration: Duração da requisição em segundos
            error: Exceção caso tenha ocorrido erro
        """
        try:
            self.request_count.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            self.response_time.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).observe(duration)
            
            if error:
                self.error_count.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=type(error).__name__
                ).inc()
                
        except Exception as e:
            logger.error(f"Error tracking metrics: {str(e)}")

    def measure_time(self, method: str, endpoint: str):
        """
        Decorator para medir tempo de execução de endpoints.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    self.active_requests.labels(endpoint=endpoint).inc()
                    response = await func(*args, **kwargs)
                    status = str(getattr(response, 'status_code', 200))
                    error = None
                except Exception as e:
                    status = "500"
                    error = e
                    raise
                finally:
                    duration = time.time() - start_time
                    self.active_requests.labels(endpoint=endpoint).dec()
                    self.track_request(method, endpoint, status, duration, error)
                
                return response
            return wrapper
        return decorator

# Instância global do coletor de métricas
metrics = MetricsCollector()

# Exemplo de uso
"""
@metrics.measure_time("GET", "/api/users")
async def get_users():
    # Lógica do endpoint
    pass
"""
