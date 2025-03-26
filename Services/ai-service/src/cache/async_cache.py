import aioredis
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AsyncCache:
    async def get_redis():
        return await aioredis.from_url("redis://localhost")

    async def set_cache(key: str, value: str, ttl: int = 300):
        redis = await AsyncCache.get_redis()
        await redis.setex(key, ttl, value)

    async def get_cache(key: str):
        redis = await AsyncCache.get_redis()
        return await redis.get(key)

async_cache = AsyncCache()
class AsyncCache:
    def __init__(self, redis_url: str = "redis://localhost", pool_size: int = 10, max_retries: int = 3):
        self._redis_url = redis_url
        self._pool_size = pool_size
        self._max_retries = max_retries
        self._pool = None

    async def _get_connection(self) -> aioredis.Redis:
        if self._pool is None:
            self._pool = await aioredis.from_url(
                self._redis_url,
                max_connections=self._pool_size,
                decode_responses=True
            )
        return self._pool

    async def set_cache(self, key: str, value: str, ttl: int = 300) -> bool:
        try:
            redis = await self._get_connection()
            return await redis.setex(key, ttl, value)
        except aioredis.RedisError as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def get_cache(self, key: str) -> Optional[str]:
        try:
            redis = await self._get_connection()
            return await redis.get(key)
        except aioredis.RedisError as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def delete_cache(self, key: str) -> bool:
        try:
            redis = await self._get_connection()
            return bool(await redis.delete(key))
        except aioredis.RedisError as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None