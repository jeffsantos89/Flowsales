import secrets
import time
from typing import Optional, Dict
from fastapi import Request, HTTPException
import logging
from datetime import datetime, timedelta
from functools import lru_cache

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSRFProtection:
    def __init__(self, secret_key: Optional[str] = None, token_expiry: int = 3600):
        """
        Initialize CSRF Protection
        :param secret_key: Optional custom secret key
        :param token_expiry: Token expiry time in seconds (default 1 hour)
        """
        self._secret_key = secret_key or secrets.token_hex(32)
        self._token_expiry = token_expiry
        self._tokens: Dict[str, float] = {}
        self._max_tokens = 1000  # Limite máximo de tokens armazenados

    @lru_cache(maxsize=128)
    def generate_token(self) -> str:
        """Generate a new CSRF token"""
        token = secrets.token_urlsafe(32)
        self._clean_expired_tokens()
        self._tokens[token] = time.time()
        return token

    def _clean_expired_tokens(self) -> None:
        """Remove expired tokens"""
        current_time = time.time()
        self._tokens = {
            token: timestamp
            for token, timestamp in self._tokens.items()
            if current_time - timestamp < self._token_expiry
        }

        # Se ainda houver muitos tokens, remova os mais antigos
        if len(self._tokens) > self._max_tokens:
            sorted_tokens = sorted(self._tokens.items(), key=lambda x: x[1])
            self._tokens = dict(sorted_tokens[-self._max_tokens:])

    async def verify_csrf_token(self, request: Request) -> None:
        """
        Verify CSRF token from request
        :raises HTTPException: If token is invalid or missing
        """
        try:
            csrf_token = request.headers.get("X-CSRF-Token")
            
            if not csrf_token:
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token missing"
                )

            if csrf_token not in self._tokens:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid CSRF token"
                )

            token_age = time.time() - self._tokens[csrf_token]
            if token_age > self._token_expiry:
                del self._tokens[csrf_token]
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token expired"
                )

            # Log successful validation
            logger.info(
                f"CSRF validation successful for {request.client.host} - "
                f"Method: {request.method} Path: {request.url.path}"
            )

        except Exception as e:
            # Log failed attempts
            logger.error(
                f"CSRF validation failed for {request.client.host} - "
                f"Method: {request.method} Path: {request.url.path} - Error: {str(e)}"
            )
            raise

# Instância global
csrf_protection = CSRFProtection()

# Função helper para uso como middleware
async def verify_csrf_token_middleware(request: Request):
    """Middleware function for CSRF protection"""
    await csrf_protection.verify_csrf_token(request)
