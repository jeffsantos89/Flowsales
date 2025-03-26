import redis

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_response(key, value, ttl=300):
    """ Armazena uma resposta no cache por um tempo limitado. """
    cache.setex(key, ttl, value)

def get_cached_response(key):
    """ Recupera resposta do cache, se existir. """
    return cache.get(key)

if __name__ == "__main__":
    cache_response("sales_forecast", "2000 unidades")
    print("📦 Cache recuperado:", get_cached_response("sales_forecast"))
    class CacheManager:
        def __init__(self, host='localhost', port=6379, db=0, password=None):
            try:
                self.cache = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    decode_responses=True,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                self.cache.ping()
            except redis.ConnectionError as e:
                raise ConnectionError(f"Failed to connect to Redis: {e}")

        def cache_set(self, key: str, value: str, ttl: int = 300) -> bool:
            try:
                return self.cache.setex(f"flowsale:{key}", ttl, value)
            except redis.RedisError as e:
                print(f"Error setting cache: {e}")
                return False

        def cache_get(self, key: str) -> str | None:
            try:
                return self.cache.get(f"flowsale:{key}")
            except redis.RedisError as e:
                print(f"Error getting cache: {e}")
                return None

        def cache_delete(self, key: str) -> bool:
            try:
                return bool(self.cache.delete(f"flowsale:{key}"))
            except redis.RedisError as e:
                print(f"Error deleting cache: {e}")
                return False

        def cache_clear(self) -> bool:
            try:
                return self.cache.flushdb()
            except redis.RedisError as e:
                print(f"Error clearing cache: {e}")
                return False

    if __name__ == "__main__":
        cache_manager = CacheManager()
        cache_manager.cache_set("sales_forecast", "2000 unidades")
        print("📦 Cache recuperado:", cache_manager.cache_get("sales_forecast"))