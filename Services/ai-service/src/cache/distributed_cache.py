import rediscluster
import logging
from typing import Any, Optional
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential

class DistributedCache:
    def __init__(self):
        self.cluster = rediscluster.RedisCluster(
            startup_nodes=[
                {"host": "redis-node-1", "port": "6379"},
                {"host": "redis-node-2", "port": "6379"}
            ],
            decode_responses=True
        )

    def set_cache(self, key: str, value: str, ttl: int = 300):
        self.cluster.setex(key, ttl, value)

    def get_cache(self, key: str):
        return self.cluster.get(key)

distributed_cache = DistributedCache()
logger = logging.getLogger(__name__)

class DistributedCache:
    def __init__(self, hosts: list[dict], max_connections: int = 50, retry_attempts: int = 3):
        self.cluster = rediscluster.RedisCluster(
            startup_nodes=hosts,
            decode_responses=True,
            max_connections=max_connections,
            socket_timeout=5.0,
            socket_connect_timeout=2.0,
            retry_on_timeout=True
        )
        self.retry_attempts = retry_attempts

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def set_cache(self, key: str, value: Any, ttl: int = 300) -> bool:
        try:
            self.cluster.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache for key {key}: {str(e)}")
            raise

    def get_cache(self, key: str) -> Optional[str]:
        try:
            return self.cluster.get(key)
        except Exception as e:
            logger.error(f"Error getting cache for key {key}: {str(e)}")
            return None

    def delete_cache(self, key: str) -> bool:
        try:
            return bool(self.cluster.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache for key {key}: {str(e)}")
            return False

    def health_check(self) -> bool:
        try:
            return self.cluster.ping()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

distributed_cache = DistributedCache([
    {"host": "redis-node-1", "port": "6379"},
    {"host": "redis-node-2", "port": "6379"}
])