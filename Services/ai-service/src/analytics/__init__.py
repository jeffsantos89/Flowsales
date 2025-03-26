from typing import Dict, Any, Optional, Callable, TypeVar, Generic
import logging
import os
from datetime import datetime
from functools import wraps, lru_cache
from threading import Lock
from enum import Enum
import json
from dataclasses import dataclass

"""
Analytics Service Package
Advanced analytics functionality with thread-safe configuration management.
"""

# Type hints
T = TypeVar('T')

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s [%(threadName)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Package metadata
@dataclass(frozen=True)
class PackageMetadata:
    version: str = '1.0.0'
    author: str = 'Flowsale Data Intelligence'
    status: str = 'Production'

class Environment(Enum):
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'

class AnalyticsConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

class AnalyticsConfig:
    """Thread-safe singleton configuration manager"""
    _instance = None
    _lock = Lock()
    _initialized = False
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        with self._lock:
            if not self._initialized:
                self.environment = Environment(os.getenv('ANALYTICS_ENV', 'production').lower())
                self.debug_mode = os.getenv('ANALYTICS_DEBUG', 'false').lower() == 'true'
                self.max_batch_size = int(os.getenv('ANALYTICS_BATCH_SIZE', '1000'))
                self.retry_attempts = int(os.getenv('ANALYTICS_RETRY_ATTEMPTS', '3'))
                self.timeout = int(os.getenv('ANALYTICS_TIMEOUT', '30'))
                self._initialized = True

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            'environment': self.environment.value,
            'debug_mode': self.debug_mode,
            'max_batch_size': self.max_batch_size,
            'retry_attempts': self.retry_attempts,
            'timeout': self.timeout
        }

class AnalyticsContext(Generic[T]):
    """Thread-safe context manager for analytics data"""
    _instance = None
    _lock = Lock()
    _context: Dict[str, Any] = {}

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    @classmethod
    def set(cls, key: str, value: T) -> None:
        with cls._lock:
            cls._context[key] = value

    @classmethod
    def get(cls, key: str, default: Optional[T] = None) -> Optional[T]:
        with cls._lock:
            return cls._context.get(key, default)

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._context.clear()

    @classmethod
    def snapshot(cls) -> Dict[str, Any]:
        """Create a snapshot of current context"""
        with cls._lock:
            return dict(cls._context)

def track_performance(name: Optional[str] = None):
    """Enhanced performance tracking decorator with optional naming"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = name or func.__name__
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Function {func_name} executed successfully in {execution_time:.3f} seconds",
                    extra={
                        'function': func_name,
                        'execution_time': execution_time,
                        'status': 'success'
                    }
                )
                return result
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"Function {func_name} failed after {execution_time:.3f} seconds: {str(e)}",
                    extra={
                        'function': func_name,
                        'execution_time': execution_time,
                        'status': 'error',
                        'error': str(e)
                    }
                )
                raise
        return wrapper
    return decorator

def handle_errors(retries: int = 3, delay: int = 1):
    """Enhanced error handling decorator with retry logic"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Error in {func.__name__} (attempt {attempt + 1}/{retries}): {str(e)}",
                        exc_info=True,
                        extra={
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'error': str(e)
                        }
                    )
                    if attempt == retries - 1:
                        raise
                    from time import sleep
                    sleep(delay * (attempt + 1))  # Exponential backoff
            return None
        return wrapper
    return decorator

# Initialize default configuration
config = AnalyticsConfig()
metadata = PackageMetadata()

# Export package interface
__all__ = [
    'AnalyticsConfig',
    'AnalyticsContext',
    'track_performance',
    'handle_errors',
    'config',
    'metadata',
    'Environment',
    'AnalyticsConfigError'
]
