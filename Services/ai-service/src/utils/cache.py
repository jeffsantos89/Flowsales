import os
import time
import redis
import logging
from typing import Any, Callable, Dict, Optional, Tuple, Union
from functools import wraps
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int) -> bool:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

class RedisCache(CacheBackend):
    def __init__(self, config: Dict[str, Union[str, int]]):
        try:
            self.client = redis.Redis(
                host=config.get('host', 'localhost'),
                port=int(config.get('port', 6379)),
                db=int(config.get('db', 0)),
                password=config.get('password'),
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True
            )
            self.client.ping()  # Test connection
        except (redis.ConnectionError, ValueError) as e:
            logger.error(f"Redis connection failed: {str(e)}")
            raise

    def get(self, key: str) -> Optional[Any]:
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis get error: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: int) -> bool:
        try:
            return bool(self.client.setex(key, ttl, value))
        except redis.RedisError as e:
            logger.error(f"Redis set error: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False

class MemoryCache(CacheBackend):
    def __init__(self):
        self._cache: Dict[str, Tuple[float, Any]] = {}

    def _cleanup(self):
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if v[0] < now]
        for k in expired_keys:
            del self._cache[k]

    def get(self, key: str) -> Optional[Any]:
        self._cleanup()
        if key in self._cache:
            expire_time, value = self._cache[key]
            if time.time() < expire_time:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int) -> bool:
        self._cleanup()
        self._cache[key] = (time.time() + ttl, value)
        return True

    def delete(self, key: str) -> bool:
        return bool(self._cache.pop(key, None))

class CacheManager:
    def __init__(self, backend: str = 'redis'):
        self.backend = self._create_backend(backend)

    def _create_backend(self, backend_type: str) -> CacheBackend:
        if backend_type == 'redis':
            config = {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': os.getenv('REDIS_PORT', 6379),
                'db': os.getenv('REDIS_DB', 0),
                'password': os.getenv('REDIS_PASSWORD')
            }
            return RedisCache(config)
        elif backend_type == 'memory':
            return MemoryCache()
        else:
            raise ValueError(f"Unsupported cache backend: {backend_type}")

    def cache_decorator(self, ttl: int = 60, prefix: str = ''):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = self.backend.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result

                # Execute function and cache result
                result = func(*args, **kwargs)
                self.backend.set(cache_key, result, ttl)
                logger.debug(f"Cache miss for key: {cache_key}")
                return result

            return wrapper
        return decorator

# Exemplo de uso:
# cache_manager = CacheManager(backend='redis')
# 
# @cache_manager.cache_decorator(ttl=300, prefix='my_app')
# def expensive_operation(param1, param2):
#     # ... código da operação ...
#     return result