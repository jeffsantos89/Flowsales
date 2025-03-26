import redis
import os
import logging
from typing import Optional
from redis.retry.default import Retry
from redis.retry.backoff import ExponentialBackoff
from redis.exceptions import RedisError
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisConfig:
    """Redis configuration class"""
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "redis")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.db = int(os.getenv("REDIS_DB", 0))
        self.password = os.getenv("REDIS_PASSWORD")
        self.socket_timeout = float(os.getenv("REDIS_SOCKET_TIMEOUT", 5.0))
        self.socket_connect_timeout = float(os.getenv("REDIS_CONNECT_TIMEOUT", 2.0))
        self.max_retries = int(os.getenv("REDIS_MAX_RETRIES", 3))
        self.decode_responses = True
        self.health_check_interval = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", 30))

def redis_error_handler(func):
    """Decorator for handling Redis errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RedisError as e:
            logger.error(f"Redis operation failed: {str(e)}")
            raise
    return wrapper

class RedisClient:
    _instance: Optional['RedisClient'] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Redis client with retry mechanism"""
        config = RedisConfig()
        retry = Retry(ExponentialBackoff(), config.max_retries)

        try:
            self._client = redis.Redis(
                host=config.host,
                port=config.port,
                db=config.db,
                password=config.password,
                socket_timeout=config.socket_timeout,
                socket_connect_timeout=config.socket_connect_timeout,
                retry=retry,
                decode_responses=config.decode_responses,
                health_check_interval=config.health_check_interval
            )
            self._check_connection()
            logger.info("Redis client initialized successfully")
        except RedisError as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            raise

    def _check_connection(self) -> None:
        """Verify Redis connection"""
        try:
            self._client.ping()
        except RedisError as e:
            logger.error(f"Redis connection check failed: {str(e)}")
            raise

    @redis_error_handler
    def get_client(self) -> redis.Redis:
        """Get Redis client instance"""
        if not self._client:
            self._initialize_client()
        return self._client

    def close(self) -> None:
        """Close Redis connection"""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except RedisError as e:
                logger.error(f"Error closing Redis connection: {str(e)}")

# Global Redis client instance
redis_client = RedisClient().get_client()

# Cleanup handler
import atexit
atexit.register(lambda: RedisClient().close())
