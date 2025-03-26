# Caminho: src/ai/queue/__init__.py

"""
Módulo central de filas da plataforma Flowsale.
Expõe backends compatíveis com Redis, Kafka, e interface abstrata para testes e extensões.
"""

from ai.queue.base import MessageQueue, Message
from ai.queue.redis_backend import RedisQueueBackend
from ai.queue.kafka_backend import KafkaQueueBackend
from typing import Type, Dict, Optional
from functools import lru_cache

__all__ = [
    "MessageQueue",
    "Message",
    "RedisQueueBackend",
    "KafkaQueueBackend"
]


class QueueFactory:
    """Factory for creating queue instances with automatic backend selection."""
    
    _backends: Dict[str, Type[MessageQueue]] = {
        'redis': RedisQueueBackend,
        'kafka': KafkaQueueBackend
    }

    @classmethod
    @lru_cache(maxsize=None)
    def create(cls, backend_type: str, **config) -> MessageQueue:
        """Creates and caches queue instances."""
        if backend_type not in cls._backends:
            raise ValueError(f"Unsupported backend: {backend_type}")
        return cls._backends[backend_type](**config)

    @classmethod
    def register_backend(cls, name: str, backend_class: Type[MessageQueue]) -> None:
        """Registers new queue backend implementations."""
        cls._backends[name] = backend_class

__version__ = '1.0.0'
DEFAULT_BACKEND = 'redis'

def create_queue(backend_type: Optional[str] = None, **config) -> MessageQueue:
    """Convenience function to create queue instances."""
    return QueueFactory.create(backend_type or DEFAULT_BACKEND, **config)