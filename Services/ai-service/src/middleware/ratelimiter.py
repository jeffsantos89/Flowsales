import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from redis import Redis
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuração do Rate Limiter"""
    requests_per_minute: int = 60
    burst_limit: int = 100
    trusted_ips: set[str] = frozenset()
    cache_ttl: int = 60

class CustomRateLimiter:
    """Implementação personalizada de Rate Limiter com cache Redis"""
    
    def __init__(self, config: RateLimitConfig, redis_client: Redis):
        self.config = config
        self.redis = redis_client
        self.limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{config.requests_per_minute}/minute"]
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def check_rate_limit(self, request: Request) -> None:
        """Verifica limites de taxa com retry exponential backoff"""
        client_ip = request.client.host
        
        # Bypass para IPs confiáveis
        if client_ip in self.config.trusted_ips:
            return
        
        # Verificar cache
        cache_key = f"ratelimit:{client_ip}"
        if await self.redis.exists(cache_key):
            return
            
        try:
            self.limiter.check(request)
            await self._update_stats(request)
        except Exception as e:
            logger.error(f"Rate limit exceeded for IP {client_ip}: {str(e)}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
                headers={
                    "Retry-After": str(self._get_retry_after()),
                    "X-RateLimit-Remaining": str(self._get_remaining(request))
                }
            )
            
    async def _update_stats(self, request: Request) -> None:
        """Atualiza estatísticas de uso"""
        remaining, reset = self.limiter.get_window_stats(request)
        request.state.rate_limit_remaining = remaining
        request.state.rate_limit_reset = reset
        
        if remaining < 3:
            logger.warning(f"Rate limit near exceeded for IP {request.client.host}")
            
    def _get_retry_after(self) -> int:
        """Calcula tempo para próxima tentativa"""
        return 60  # Simplificado - pode ser mais sofisticado
        
    def _get_remaining(self, request: Request) -> int:
        """Obtém requisições restantes"""
        return self.limiter.get_window_stats(request)[0]

class BackgroundTaskManager:
    """Gerenciador de tarefas em background com pool de threads"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self._pool = threading.ThreadPool(max_workers)
        
    def background_task(self, func: Callable) -> Callable:
        """Decorator para execução assíncrona de tarefas"""
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            self._pool.apply_async(
                self._safe_run,
                args=(func, args, kwargs),
                error_callback=self._handle_error
            )
        return wrapper
        
    def _safe_run(self, func: Callable, args: tuple, kwargs: dict) -> Any:
        """Executa função com tratamento de erros"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in background task {func.__name__}: {e}")
            
    def _handle_error(self, error: Exception) -> None:
        """Tratamento centralizado de erros"""
        logger.error(f"Background task failed: {error}")
        
    def shutdown(self) -> None:
        """Finaliza pool de threads graciosamente"""
        self._pool.close()
        self._pool.join()

# Exemplo de uso
rate_limiter = CustomRateLimiter(
    config=RateLimitConfig(),
    redis_client=Redis(host='localhost', port=6379)
)

task_manager = BackgroundTaskManager()

async def rate_limit_middleware(request: Request) -> None:
    """Middleware de rate limiting"""
    await rate_limiter.check_rate_limit(request)
