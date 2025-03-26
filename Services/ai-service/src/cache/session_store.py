import json
from redis_client import redis_client
import logging
from typing import Optional, Any, Dict
from functools import wraps
from redis.exceptions import RedisError

class SessionStore:
    @staticmethod
    def create_session(user_id: str, session_data: dict, ttl: int = 3600):
        redis_client.setex(f"session:{user_id}", ttl, json.dumps(session_data))

    @staticmethod
    def get_session(user_id: str):
        session = redis_client.get(f"session:{user_id}")
        return json.loads(session) if session else None

    @staticmethod
    def delete_session(user_id: str):
        redis_client.delete(f"session:{user_id}")

session_store = SessionStore()
logger = logging.getLogger(__name__)

class SessionStoreException(Exception):
    pass

class SessionStore:
    PREFIX = "session:"
    DEFAULT_TTL = 3600

    @staticmethod
    def _handle_redis_error(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RedisError as e:
                logger.error(f"Redis operation failed: {str(e)}")
                raise SessionStoreException(f"Session store operation failed: {str(e)}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                raise SessionStoreException("Invalid session data format")
        return wrapper

    @classmethod
    def _get_session_key(cls, user_id: str) -> str:
        return f"{cls.PREFIX}{user_id}"

    @classmethod
    @_handle_redis_error
    def create_session(cls, user_id: str, session_data: Dict[str, Any], ttl: int = DEFAULT_TTL) -> None:
        if not isinstance(session_data, dict):
            raise ValueError("Session data must be a dictionary")
        redis_client.setex(cls._get_session_key(user_id), ttl, json.dumps(session_data))
        logger.debug(f"Created session for user {user_id}")

    @classmethod
    @_handle_redis_error
    def get_session(cls, user_id: str) -> Optional[Dict[str, Any]]:
        session = redis_client.get(cls._get_session_key(user_id))
        if session:
            logger.debug(f"Retrieved session for user {user_id}")
            return json.loads(session)
        logger.debug(f"No session found for user {user_id}")
        return None

    @classmethod
    @_handle_redis_error
    def delete_session(cls, user_id: str) -> None:
        redis_client.delete(cls._get_session_key(user_id))
        logger.debug(f"Deleted session for user {user_id}")

    @classmethod
    @_handle_redis_error
    def update_session_ttl(cls, user_id: str, ttl: int = DEFAULT_TTL) -> bool:
        return bool(redis_client.expire(cls._get_session_key(user_id), ttl))

session_store = SessionStore()