import logging
from typing import Any, Optional, Union
from functools import wraps
import pickle
import zlib
from redis.exceptions import RedisError
from redis_client import redis_client

logger = logging.getLogger(__name__)

class CacheException(Exception):
    """Custom exception for cache operations"""
    pass

class CacheManager:
    def __init__(self, default_ttl: int = 300, compression: bool = True):
        """
        Initialize CacheManager with default settings
        
        Args:
            default_ttl (int): Default time-to-live in seconds
            compression (bool): Enable/disable data compression
        """
        self.default_ttl = default_ttl
        self.compression = compression

    def _serialize(self, value: Any) -> bytes:
        """Serialize and optionally compress data"""
        try:
            serialized = pickle.dumps(value)
            if self.compression:
                return zlib.compress(serialized)
            return serialized
        except Exception as e:
            logger.error(f"Serialization error: {str(e)}")
            raise CacheException(f"Failed to serialize data: {str(e)}")

    def _deserialize(self, value: bytes) -> Any:
        """Deserialize and optionally decompress data"""
        if value is None:
            return None
        try:
            if self.compression:
                value = zlib.decompress(value)
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Deserialization error: {str(e)}")
            raise CacheException(f"Failed to deserialize data: {str(e)}")

    def set_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache with error handling
        
        Returns:
            bool: Success status
        """
        try:
            ttl = ttl or self.default_ttl
            serialized_value = self._serialize(value)
            redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Successfully cached key: {key}")
            return True
        except RedisError as e:
            logger.error(f"Redis error while setting cache: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while setting cache: {str(e)}")
            return False

    def get_cache(self, key: str, default: Any = None) -> Any:
        """
        Get a value from cache with error handling
        
        Returns:
            Any: Cached value or default if not found
        """
        try:
            value = redis_client.get(key)
            if value is None:
                return default
            return self._deserialize(value)
        except RedisError as e:
            logger.error(f"Redis error while getting cache: {str(e)}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error while getting cache: {str(e)}")
            return default

    def delete_cache(self, key: str) -> bool:
        """
        Delete a key from cache
        
        Returns:
            bool: Success status
        """
        try:
            result = redis_client.delete(key)
            logger.debug(f"Successfully deleted key: {key}")
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis error while deleting cache: {str(e)}")
            return False

    def clear_all_cache(self) -> bool:
        """
        Clear all cache with confirmation
        
        Returns:
            bool: Success status
        """
        try:
            redis_client.flushall()
            logger.warning("Cache cleared completely")
            return True
        except RedisError as e:
            logger.error(f"Redis error while clearing cache: {str(e)}")
            return False

    def cache_decorator(self, ttl: Optional[int] = None):
        """
        Decorator for caching function results
        
        Usage:
            @cache_manager.cache_decorator(ttl=300)
            def expensive_function(param):
                return expensive_computation(param)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"cache:{func.__name__}:{str(args)}:{str(kwargs)}"
                result = self.get_cache(cache_key)
                if result is None:
                    result = func(*args, **kwargs)
                    self.set_cache(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

# Singleton instance
cache_manager = CacheManager()
