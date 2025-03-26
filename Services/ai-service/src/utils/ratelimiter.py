# src/ai/utils/ratelimiter.py

import time
import threading
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Estratégias de rate limiting"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"

@dataclass
class RateLimitConfig:
    """Configuração do rate limiter"""
    max_requests: int
    time_window: int
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_size: Optional[int] = None

class RateLimitExceeded(Exception):
    """Exceção levantada quando o limite de taxa é excedido."""
    def __init__(self, message: str, retry_after: float):
        self.retry_after = retry_after
        super().__init__(message)

class RateLimiter:
    def __init__(self, config: RateLimitConfig):
        """
        Inicializa o RateLimiter com configurações avançadas.

        Args:
            config (RateLimitConfig): Configurações do rate limiter
        """
        self.config = config
        self.lock = threading.Lock()
        self.request_times: List[float] = []
        self._last_cleanup: float = time.time()
        self._cleanup_interval: int = min(60, self.config.time_window)
        self._token_bucket: float = config.max_requests if config.strategy == RateLimitStrategy.TOKEN_BUCKET else 0
        self._last_token_refresh: float = time.time()
        
        # Cache para métricas
        self._metrics: Dict[str, int] = {
            "total_requests": 0,
            "rejected_requests": 0,
            "current_usage": 0
        }

    def _refresh_tokens(self) -> None:
        """Atualiza tokens para estratégia TOKEN_BUCKET"""
        if self.config.strategy != RateLimitStrategy.TOKEN_BUCKET:
            return

        now = time.time()
        elapsed = now - self._last_token_refresh
        new_tokens = (elapsed * self.config.max_requests) / self.config.time_window
        self._token_bucket = min(
            self.config.max_requests,
            self._token_bucket + new_tokens
        )
        self._last_token_refresh = now

    def _cleanup(self) -> None:
        """Limpa requisições antigas e atualiza métricas"""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        with self.lock:
            self.request_times = [t for t in self.request_times if now - t < self.config.time_window]
            self._metrics["current_usage"] = len(self.request_times)
            self._last_cleanup = now

    def get_retry_after(self) -> float:
        """Calcula tempo de espera para próxima tentativa"""
        if not self.request_times:
            return 0
        return max(0, self.config.time_window - (time.time() - self.request_times[0]))

    def _check_rate_limit(self) -> None:
        """Verifica se o limite de taxa foi excedido"""
        now = time.time()
        self._cleanup()

        with self.lock:
            self._metrics["total_requests"] += 1

            if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                self._refresh_tokens()
                if self._token_bucket < 1:
                    self._metrics["rejected_requests"] += 1
                    raise RateLimitExceeded(
                        "Taxa limite excedida",
                        self.get_retry_after()
                    )
                self._token_bucket -= 1
            else:
                if len(self.request_times) >= self.config.max_requests:
                    self._metrics["rejected_requests"] += 1
                    raise RateLimitExceeded(
                        "Taxa limite excedida",
                        self.get_retry_after()
                    )
            self.request_times.append(now)

    @contextmanager
    def __call__(self):
        """Contexto síncrono para rate limiting"""
        try:
            self._check_rate_limit()
            yield
        except RateLimitExceeded as e:
            logger.warning(f"Rate limit excedido. Retry after: {e.retry_after:.2f}s")
            raise

    async def acquire_async(self):
        """Versão assíncrona do rate limiter"""
        try:
            self._check_rate_limit()
        except RateLimitExceeded as e:
            await asyncio.sleep(e.retry_after)
            self._check_rate_limit()

    def get_metrics(self) -> Dict[str, int]:
        """Retorna métricas do rate limiter"""
        return self._metrics.copy()

    @classmethod
    def decorator(cls, config: RateLimitConfig):
        """Decorator para rate limiting em funções"""
        limiter = cls(config)

        def decorator(func):
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with limiter():
                    return func(*args, **kwargs)

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                await limiter.acquire_async()
                return await func(*args, **kwargs)

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
