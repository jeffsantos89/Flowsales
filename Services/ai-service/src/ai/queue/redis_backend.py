import aioredis
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, Generic
import logging
import asyncio
from datetime import datetime, timedelta
from functools import wraps
import backoff
from dataclasses import dataclass, field
from enum import Enum
import orjson
import uuid
from contextlib import asynccontextmanager
from prometheus_client import Counter, Histogram, Gauge, Summary
import aiocache
import asyncio.exceptions
from typing_extensions import Protocol
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
import socket
import signal

T = TypeVar('T')
logger = structlog.get_logger(__name__)

class QueuePriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class QueueError(Exception): pass
class ConnectionError(QueueError): pass
class MessageValidationError(QueueError): pass
class QueueTimeoutError(QueueError): pass
class QueueFullError(QueueError): pass

@dataclass
class QueueConfig:
    redis_url: str
    queue_prefix: str = "queue"
    max_retries: int = 3
    connection_timeout: float = 5.0
    max_pool_size: int = 50
    cache_ttl: int = 300
    message_ttl: int = 86400  # 24 hours
    batch_size: int = 100
    max_queue_size: int = 10000
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

class MessageHandler(Protocol, Generic[T]):
    async def __call__(self, message: T) -> None: ...

class RedisMetrics:
    """Enhanced metrics for better monitoring"""
    messages_processed = Counter('queue_messages_processed_total', 'Total messages processed', ['priority', 'status'])
    processing_time = Histogram('queue_processing_time_seconds', 'Message processing time', ['type'])
    queue_size = Gauge('queue_size', 'Current queue size', ['priority'])
    error_count = Counter('queue_errors_total', 'Total errors', ['type'])
    message_age = Histogram('queue_message_age_seconds', 'Message age before processing')
    circuit_breaker_state = Gauge('queue_circuit_breaker_state', 'Circuit breaker state (0=open, 1=closed)')
    worker_count = Gauge('queue_worker_count', 'Number of active workers')

@dataclass
class QueueMessage:
    id: str
    type: str
    user_id: str
    payload: Dict[str, Any]
    priority: QueuePriority
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3
    version: str = "1.0"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def create(cls, type: str, user_id: str, payload: Dict[str, Any], 
               priority: QueuePriority = QueuePriority.MEDIUM) -> 'QueueMessage':
        return cls(
            id=str(uuid.uuid4()),
            type=type,
            user_id=user_id,
            payload=payload,
            priority=priority,
            timestamp=datetime.utcnow()
        )

class CircuitBreaker:
    def __init__(self, threshold: int, timeout: int):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.utcnow()
        if self.failures >= self.threshold:
            self.state = "open"
            RedisMetrics.circuit_breaker_state.set(0)

    def reset(self):
        self.failures = 0
        self.state = "closed"
        RedisMetrics.circuit_breaker_state.set(1)

class RedisQueueBackend:
    def __init__(self, config: QueueConfig):
        self.config = config
        self.redis: Optional[aioredis.Redis] = None
        self.is_connected = False
        self._lock = asyncio.Lock()
        self._cache = aiocache.Cache(aiocache.SimpleMemoryCache, ttl=config.cache_ttl)
        self._message_handlers: Dict[str, MessageHandler] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._circuit_breaker = CircuitBreaker(
            config.circuit_breaker_threshold,
            config.circuit_breaker_timeout
        )
        self._shutdown_event = asyncio.Event()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info("Received shutdown signal", signal=signum)
        self._shutdown_event.set()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def connect(self):
        if not self.is_connected:
            try:
                self.redis = await aioredis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    max_connections=self.config.max_pool_size,
                    socket_timeout=self.config.connection_timeout,
                    socket_connect_timeout=self.config.connection_timeout,
                    retry_on_timeout=True
                )
                self.is_connected = True
                self._circuit_breaker.reset()
                await self._start_cleanup_task()
            except Exception as e:
                self._circuit_breaker.record_failure()
                logger.error("Redis connection failed", error=str(e))
                raise ConnectionError(f"Could not connect to Redis: {e}")

    async def _health_check(self) -> bool:
        try:
            if self.redis:
                await self.redis.ping()
                return True
        except Exception:
            return False
        return False

    async def process_message(self, message: QueueMessage) -> QueueOperationStatus:
        handler = self._message_handlers.get(message.type)
        if not handler:
            logger.error("No handler for message type", message_type=message.type)
            return QueueOperationStatus.ERROR

        try:
            with RedisMetrics.processing_time.labels(message.type).time():
                await handler(message)
                RedisMetrics.messages_processed.labels(
                    priority=message.priority.name,
                    status="success"
                ).inc()
            return QueueOperationStatus.SUCCESS
        except Exception as e:
            logger.error(
                "Message processing failed",
                error=str(e),
                message_id=message.id,
                retry_count=message.retry_count
            )
            if message.retry_count < message.max_retries:
                message.retry_count += 1
                await self.send(message, message.priority)
                return QueueOperationStatus.RETRY
            RedisMetrics.messages_processed.labels(
                priority=message.priority.name,
                status="error"
            ).inc()
            return QueueOperationStatus.ERROR

    async def start_processing(self, worker_count: int = 3):
        RedisMetrics.worker_count.set(worker_count)
        workers = [self._worker(i) for i in range(worker_count)]
        try:
            await asyncio.gather(*workers)
        except Exception as e:
            logger.error("Worker pool error", error=str(e))
        finally:
            RedisMetrics.worker_count.set(0)

