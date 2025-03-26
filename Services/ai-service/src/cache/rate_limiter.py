import time
from typing import Optional, Tuple
from datetime import datetime
from redis.exceptions import RedisError
from redis_client import redis_client
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self._default_max_requests = 100
        self._default_window = 60
        self._redis_timeout = 2  # seconds

    async def is_rate_limited(
        self, 
        ip: str, 
        max_requests: Optional[int] = None, 
        window: Optional[int] = None
    ) -> Tuple[bool, dict]:
        """
        Check if a request should be rate limited.
        
        Args:
            ip: The IP address to check
            max_requests: Maximum requests allowed in the window
            window: Time window in seconds
            
        Returns:
            Tuple[bool, dict]: (is_limited, rate_limit_info)
        """
        try:
            max_requests = max_requests or self._default_max_requests
            window = window or self._default_window
            
            pipe = redis_client.pipeline()
            current_time = int(time.time())
            window_key = f"ratelimit:{ip}:{current_time // window}"
            
            # Atomic operations using pipeline
            pipe.incr(window_key)
            pipe.expire(window_key, window)
            current_requests = pipe.execute()[0]

            rate_limit_info = {
                "limit": max_requests,
                "remaining": max(0, max_requests - current_requests),
                "reset": (current_time // window * window) + window,
                "current": current_requests
            }

            is_limited = current_requests > max_requests
            
            if is_limited:
                logger.warning(f"Rate limit exceeded for IP: {ip}")
            
            return is_limited, rate_limit_info

        except RedisError as e:
            logger.error(f"Redis error in rate limiter: {str(e)}")
