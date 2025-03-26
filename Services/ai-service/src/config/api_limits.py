from dataclasses import dataclass
from typing import Optional
import os

class APILimits:
    RATE_LIMIT_PER_MINUTE = 100  # 100 requisições por minuto
    MAX_PAYLOAD_SIZE_MB = 5  # Tamanho máximo permitido por requisição
    TIMEOUT_SECONDS = 30  # Tempo limite de resposta

api_limits = APILimits()
@dataclass
class APILimitsConfig:
    rate_limit_per_minute: int
    max_payload_size_mb: int
    timeout_seconds: int
    max_concurrent_requests: int = 50
    retry_attempts: int = 3
    backoff_factor: float = 0.5
    circuit_breaker_threshold: int = 5

class APILimits:
    def __init__(self):
        self.config = APILimitsConfig(
            rate_limit_per_minute=int(os.getenv('API_RATE_LIMIT', 100)),
            max_payload_size_mb=int(os.getenv('API_MAX_PAYLOAD_SIZE', 5)),
            timeout_seconds=int(os.getenv('API_TIMEOUT', 30)),
            max_concurrent_requests=int(os.getenv('API_MAX_CONCURRENT', 50)),
            retry_attempts=int(os.getenv('API_RETRY_ATTEMPTS', 3)),
            backoff_factor=float(os.getenv('API_BACKOFF_FACTOR', 0.5)),
            circuit_breaker_threshold=int(os.getenv('API_CIRCUIT_BREAKER', 5))
        )

    def get_config(self) -> APILimitsConfig:
        return self.config

api_limits = APILimits()