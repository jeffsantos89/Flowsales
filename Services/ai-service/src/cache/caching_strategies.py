from functools import wraps
from typing import Any, Callable, Optional, Union
from datetime import timedelta
import logging
from cache_manager import cache_manager

logger = logging.getLogger(__name__)

class CacheError(Exception):
    """Base exception for caching operations"""
    pass

class CachingStrategies:
    """Handles different caching strategies with error handling and logging"""

    @staticmethod
    def cache_first_fetch_later(
        key: str,
        fetch_func: Callable[[], Any],
        ttl: Union[int, timedelta] = 300,
        max_retries: int = 3
    ) -> Any:
        """
        Retrieve data from cache first, if not found fetch from source
        
        Args:
            key: Cache key
            fetch_func: Function to fetch data if not in cache
            ttl: Time to live in seconds or timedelta
            max_retries: Maximum number of retries for fetch operation
        
        Returns:
            Cached or fetched data
        
        Raises:
            CacheError: If both cache and fetch operations fail
        """
        try:
            data = cache_manager.get_cache(key)
            if data is not None:
                logger.debug(f"Cache hit for key: {key}")
                return data
            
            logger.debug(f"Cache miss for key: {key}")
            for attempt in range(max_retries):
                try:
                    data = fetch_func()
                    if data is not None:
                        ttl_seconds = ttl.total_seconds() if isinstance(ttl, timedelta) else ttl
                        cache_manager.set_cache(key, data, int(ttl_seconds))
                        return data
                except Exception as e:
                    logger.error(f"Fetch attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise CacheError(f"Failed to fetch data after {max_retries} attempts") from e
            
            raise CacheError("Fetch function returned None")
            
        except Exception as e:
            logger.error(f"Cache operation failed for key {key}: {str(e)}")
            raise CacheError(f"Cache operation failed: {str(e)}") from e

    @staticmethod
    def write_through_cache(
        key: str,
        value: Any,
        ttl: Union[int, timedelta] = 300,
        validate: Optional[Callable[[Any], bool]] = None
    ) -> None:
        """
        Write data through cache with validation
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds or timedelta
            validate: Optional validation function
        
        Raises:
            CacheError: If validation or cache operation fails
        """
        try:
            if validate and not validate(value):
                raise CacheError(f"Validation failed for key: {key}")
            
            ttl_seconds = ttl.total_seconds() if isinstance(ttl, timedelta) else ttl
            cache_manager.set_cache(key, value, int(ttl_seconds))
            logger.debug(f"Successfully cached value for key: {key}")
            
        except Exception as e:
            logger.error(f"Failed to write through cache for key {key}: {str(e)}")
            raise CacheError(f"Write through cache failed: {str(e)}") from e

def cache_decorator(
    key_prefix: str,
    ttl: Union[int, timedelta] = 300
) -> Callable:
    """
    Decorator for automatic caching of function results
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds or timedelta
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            return CachingStrategies.cache_first_fetch_later(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl
            )
        return wrapper
    return decorator

# Singleton instance
caching_strategies = CachingStrategies()
