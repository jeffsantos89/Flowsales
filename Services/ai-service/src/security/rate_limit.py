from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime
from typing import Dict, Optional
from functools import wraps
from redis import Redis

# Configuração de rate-limiting para proteção contra ataques
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100 per minute")
def rate_limited_endpoint():
    return {"message": "Requisição limitada"}
    class RateLimiter:
        def __init__(self, redis_client: Redis):
            self.limiter = limiter
            self.redis_client = redis_client
            
        def dynamic_limit(self, user_tier: str = "basic"):
            limits = {
                "basic": "100 per minute",
                "premium": "500 per minute",
                "enterprise": "1000 per minute"
            }
            
            def decorator(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    try:
                        current_limit = limits.get(user_tier, limits["basic"])
                        @self.limiter.limit(current_limit)
                        def limited_func():
                            return func(*args, **kwargs)
                        return limited_func()
                    except Exception as e:
                        self.log_rate_limit_event(str(e))
                        return {"error": "Rate limit exceeded", "retry_after": "60 seconds"}, 429
                return wrapper
            return decorator
        
        def log_rate_limit_event(self, error: str) -> None:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "error": error,
                "ip": get_remote_address()
            }
            self.redis_client.lpush("rate_limit_logs", str(event))

        def get_metrics(self) -> Dict:
            return {
                "total_requests": self.redis_client.get("total_requests"),
                "blocked_requests": self.redis_client.get("blocked_requests")
            }