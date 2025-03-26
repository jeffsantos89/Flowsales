from enum import Enum
from typing import List, Optional
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from security.auth import decode_access_token
from functools import wraps
import logging
from cachetools import TTLCache
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for token validations (TTL of 5 minutes)
token_cache = TTLCache(maxsize=100, ttl=300)

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

# Role hierarchy
ROLE_HIERARCHY = {
    Role.ADMIN: [Role.ADMIN, Role.MANAGER, Role.USER],
    Role.MANAGER: [Role.MANAGER, Role.USER],
    Role.USER: [Role.USER]
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class PermissionError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=403, detail=detail)

def validate_token(token: str) -> dict:
    """Validate and decode token with caching"""
    cache_key = f"token_{hash(token)}"
    
    if cache_key in token_cache:
        return token_cache[cache_key]
    
    try:
        payload = decode_access_token(token)
        if payload:
            token_cache[cache_key] = payload
            return payload
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise PermissionError("Token inválido ou expirado")

def get_current_user_role(token: str = Security(oauth2_scheme)) -> Role:
    """Get current user role with enhanced validation"""
    try:
        payload = validate_token(token)
        if not payload or "role" not in payload:
            raise PermissionError("Role não encontrada no token")
        
        role = payload["role"]
        if role not in [r.value for r in Role]:
            raise PermissionError("Role inválida")
        
        return Role(role)
    except Exception as e:
        logger.error(f"Error getting user role: {str(e)}")
        raise

def require_role(required_role: Role):
    """Enhanced role checker with hierarchy support"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user_role: Role = Depends(get_current_user_role), **kwargs):
            try:
                if required_role not in ROLE_HIERARCHY.get(user_role, []):
                    logger.warning(f"Access denied: User with role {user_role} tried to access {required_role} resource")
                    raise PermissionError(f"Acesso negado para role {user_role}")
                
                start_time = time.time()
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"Access granted: {user_role} accessed {func.__name__} in {duration:.2f}s")
                return result
                
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
