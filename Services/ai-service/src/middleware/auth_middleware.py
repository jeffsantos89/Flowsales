from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import os
import logging
from functools import lru_cache
from pydantic import BaseModel

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JWTConfig:
    """Configurações do JWT"""
    SECRET_KEY: str = os.getenv("JWT_SECRET")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    @classmethod
    def validate_config(cls) -> None:
        if not cls.SECRET_KEY:
            raise ValueError("JWT_SECRET environment variable is not set")

class TokenPayload(BaseModel):
    """Modelo para payload do token"""
    sub: str
    exp: datetime
    iat: datetime
    scope: str

@lru_cache()
def get_jwt_config() -> JWTConfig:
    """Retorna configuração do JWT com cache"""
    config = JWTConfig()
    config.validate_config()
    return config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def verify_jwt_token(
    token: str = Depends(oauth2_scheme),
    config: JWTConfig = Depends(get_jwt_config)
) -> Dict[str, Any]:
    """
    Middleware para validar JWT Token
    
    Args:
        token: JWT token string
        config: Configurações do JWT
    
    Returns:
        Dict contendo payload do token decodificado
    
    Raises:
        HTTPException: Quando o token é inválido ou expirado
    """
    try:
        # Decodifica o token
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
            options={"verify_exp": True}
        )
        
        # Valida o payload usando Pydantic
        token_data = TokenPayload(**payload)
        
        # Log da validação bem-sucedida
        logger.info(f"Token válido para usuário: {token_data.sub}")
        
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning(f"Token expirado recebido")
        raise HTTPException(
            status_code=401,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except jwt.InvalidTokenError as e:
        logger.error(f"Token inválido recebido: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except Exception as e:
        logger.error(f"Erro inesperado na validação do token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno no servidor durante validação do token"
        )

def create_token(subject: str, scope: str = "access") -> str:
    """
    Cria um novo JWT token
    
    Args:
        subject: Identificador do usuário
        scope: Escopo do token (access ou refresh)
        
    Returns:
        JWT token string
    """
    config = get_jwt_config()
    
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "iat": now,
        "scope": scope
    }
    
    if scope == "access":
        payload["exp"] = now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        payload["exp"] = now + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)
