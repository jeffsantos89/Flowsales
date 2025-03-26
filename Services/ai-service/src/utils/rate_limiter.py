import aioredis
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import json
from dataclasses import dataclass
from enum import Enum
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"

@dataclass
class RateLimitConfig:
    max_requests: int
    window_seconds: int
    strategy: RateLimitStrategy
    burst_multiplier: float = 1.0
    clean_interval: int = 3600  # Cleanup interval in seconds

class RateLimitInfo:
    def __init__(self, remaining: int, reset_at: float, total: int):
        self.remaining = remaining
        self.reset_at = reset_at
        self.total = total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "remaining": self.remaining,
            "reset_at": self.reset_at,
            "total": self.total
        }

class RateLimiter:
    def __init__(
        self,
        redis_client: aioredis.Redis,
        config: RateLimitConfig,
        prefix: str = "rate:limit",
        fallback_enabled: bool = True
    ):
        self.redis = redis_client
        self.config = config
        self.prefix = prefix
        self.fallback_enabled = fallback_enabled
        self._local_cache: Dict[str, RateLimitInfo] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Initialize the rate limiter and start background tasks"""
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Rate limiter started with config: %s", self.config)

    async def stop(self):
        """Cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Rate limiter stopped")

    def _key(self, user_id: str) -> str:
        return f"{self.prefix}:{self.config.strategy.value}:{user_id}"

    async def _periodic_cleanup(self):
        """Periodically clean up expired entries"""
        while True:
            try:
                await asyncio.sleep(self.config.clean_interval)
                pattern = f"{self.prefix}:*"
                async for key in self.redis.scan_iter(match=pattern):
                    if await self.redis.ttl(key) <= 0:
                        await self.redis.delete(key)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup task: %s", str(e))

    @asynccontextmanager
    async def rate_limit_context(self, user_id: str):
        """Context manager for rate limiting"""
        try:
            await self.check_limit(user_id)
            yield
        finally:
            # Cleanup or logging could be added here
            pass

    async def get_limit_info(self, user_id: str) -> RateLimitInfo:
        """Get current rate limit information for a user"""
        key = self._key(user_id)
        pipe = self.redis.pipeline()
        pipe.get(key)
        pipe.ttl(key)
        
        try:
            count, ttl = await pipe.execute()
            count = int(count) if count else 0
            remaining = max(0, self.config.max_requests - count)
            reset_at = datetime.now().timestamp() + ttl if ttl > 0 else 0
            
            return RateLimitInfo(
                remaining=remaining,
                reset_at=reset_at,
                total=self.config.max_requests
            )
        except Exception as e:
            logger.error(f"Error getting limit info: {e}")
            if self.fallback_enabled:
                return RateLimitInfo(
                    remaining=1,
                    reset_at=datetime.now().timestamp() + self.config.window_seconds,
                    total=self.config.max_requests
                )
            raise

    async def is_allowed(self, user_id: str) -> bool:
        """Check if request is allowed with improved error handling and burst support"""
        key = self._key(user_id)
        
        try:
            async with self.redis.pipeline() as pipe:
                pipe.incr(key)
                pipe.ttl(key)
                current, ttl = await pipe.execute()

                if current == 1:
                    await self.redis.expire(key, self.config.window_seconds)

                # Support for burst capacity
                effective_limit = int(self.config.max_requests * self.config.burst_multiplier)
                
                if current > effective_limit:
                    logger.warning(f"[RateLimit] Exceeded by {user_id}. TTL: {ttl}s")
                    return False

                return True

        except Exception as e:
            logger.error(f"Redis error in is_allowed: {e}")
            if self.fallback_enabled:
                logger.warning("Using fallback rate limiting")
                return True
            raise

    async def check_limit(self, user_id: str):
        """Check rate limit with enhanced error details"""
        if not await self.is_allowed(user_id):
            info = await self.get_limit_info(user_id)
            raise RateLimitExceeded(
                user_id=user_id,
                max_requests=self.config.max_requests,
                window=self.config.window_seconds,
                limit_info=info
            )

class RateLimitExceeded(Exception):
    def __init__(
        self,
        user_id: str,
        max_requests: int,
        window: int,
        limit_info: RateLimitInfo
    ):
        self.user_id = user_id
        self.max_requests = max_requests
        self.window = window
        self.timestamp = datetime.utcnow().isoformat()
        self.limit_info = limit_info

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": "rate_limit_exceeded",
            "user_id": self.user_id,
            "max_requests": self.max_requests,
            "window": self.window,
            "timestamp": self.timestamp,
            "limit_info": self.limit_info.to_dict()
        }

    def __str__(self):
        return json.dumps(self.to_dict())
