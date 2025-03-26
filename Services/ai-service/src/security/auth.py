from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.settings import settings
import logging
from enum import Enum
from dataclasses import dataclass
import secrets

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

@dataclass
class TokenConfig:
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    @classmethod
    def from_settings(cls) -> 'TokenConfig':
        return cls(
            secret_key=settings.JWT_SECRET,
            algorithm="HS256",
            access_token_expire_minutes=60,
            refresh_token_expire_days=7
        )

class SecurityManager:
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12  # Aumenta a segurança do hash
        )
        self.token_config = TokenConfig.from_settings()
        self._validate_secret_key()

    def _validate_secret_key(self) -> None:
        if len(self.token_config.secret_key) < 32:
            logger.warning("JWT secret key should be at least 32 characters long")
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False

    def hash_password(self, password: str) -> str:
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise ValueError("Failed to hash password")

    def create_token(
        self,
        data: Dict[str, Any],
        token_type: TokenType,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        try:
            to_encode = data.copy()
            
            if token_type == TokenType.ACCESS:
                expire_delta = expires_delta or timedelta(
                    minutes=self.token_config.access_token_expire_minutes
                )
            else:
                expire_delta = expires_delta or timedelta(
                    days=self.token_config.refresh_token_expire_days
                )

            expire = datetime.utcnow() + expire_delta
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": token_type.value,
                "jti": secrets.token_hex(16)  # Unique token ID
            })

            return jwt.encode(
                to_encode,
                self.token_config.secret_key,
                algorithm=self.token_config.algorithm
            )
        except Exception as e:
            logger.error(f"Error creating token: {str(e)}")
            raise ValueError("Failed to create token")

    def decode_token(
        self,
        token: str,
        verify_exp: bool = True
    ) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                self.token_config.secret_key,
                algorithms=[self.token_config.algorithm],
                options={"verify_exp": verify_exp}
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error decoding token: {str(e)}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        payload = self.decode_token(refresh_token)
        if not payload or payload.get("type") != TokenType.REFRESH.value:
            return None
        
        # Remove tipo e tempo de expiração do token atual
        del payload["type"]
        del payload["exp"]
        del payload["iat"]
        del payload["jti"]
        
        return self.create_token(payload, TokenType.ACCESS)

# Instância global do gerenciador de segurança
security = SecurityManager()
