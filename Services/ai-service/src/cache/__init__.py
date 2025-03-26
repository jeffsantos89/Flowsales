"""
Distributed, Asynchronous and Secure Caching Layer for Flowsale Platform.
Provides session management, probabilistic filters, rate limiting and custom caching strategies.

Features:
- Fully async operations
- Distributed caching with Redis
- Session management
- Rate limiting
- Bloom filters
- Custom caching strategies
- Type hints
- Performance optimized
"""

from typing import List, Type
from importlib import import_module

# Core components
from async_cache import AsyncCache
from redis_client import RedisClient 
from cache_manager import CacheManager
from distributed_cache import DistributedCache
from rate_limiter import RateLimiter
from session_store import SessionStore

# Strategy components
from caching_strategies import CachingStrategies
from bloom_filter import BloomFilter

# Version control
__version__ = "1.0.0"
__author__ = "Flowsale Team"

# Component registry
CACHE_COMPONENTS: List[Type] = [
    AsyncCache,
    RedisClient,
    CacheManager, 
    DistributedCache,
    RateLimiter,
    SessionStore,
    CachingStrategies,
    BloomFilter
]

__all__ = [component.__name__ for component in CACHE_COMPONENTS]

def initialize_cache(config: dict = None) -> CacheManager:
    """Initialize the cache system with provided configuration."""
    return CacheManager.initialize(config or {})

# Lazy loading of components
def get_component(name: str):
    """Lazy load cache components when needed."""
    return import_module(f"ai.cache.{name}")
