from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import jwt
from jwt.exceptions import JWTError, ExpiredSignatureError, InvalidTokenError
from .config import settings
from logging import getLogger
from functools import lru_cache
from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer

router = APIRouter()

logger = getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12  # Aumenta a segurança do hash
        )
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    @lru_cache(maxsize=1024)
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta usando cache para melhor performance."""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {str(e)}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Gera um hash seguro para a senha."""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Erro ao gerar hash da senha: {str(e)}")
            raise ValueError("Erro ao processar senha")

    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Cria um token JWT com validação de expiração e dados adicionais de segurança.
        """
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + (
                expires_delta 
                if expires_delta 
                else timedelta(minutes=self.access_token_expire_minutes)
            )
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),  # Quando o token foi emitido
                "type": "access_token"
            })
            
            return jwt.encode(
                to_encode, 
                self.secret_key, 
                algorithm=self.algorithm
            )
        except Exception as e:
            logger.error(f"Erro ao criar token: {str(e)}")
            raise ValueError("Erro ao gerar token de acesso")

    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Valida e decodifica o token JWT, retornando as informações do usuário.
        Inclui tratamento de diversos tipos de erros e logging.
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Validações adicionais
            if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
                logger.warning(f"Token expirado para usuário: {payload.get('sub')}")
                return None

            return {
                "username": payload.get("sub"),
                "exp": payload.get("exp"),
                "type": payload.get("type")
            }

        except ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except InvalidTokenError:
            logger.warning("Token inválido")
            return None
        except JWTError as e:
            logger.error(f"Erro JWT: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao processar token: {str(e)}")
            return None

# Instância global do gerenciador de segurança
security_manager = SecurityManager()

# Funções de conveniência para manter compatibilidade com código existente
auth = HTTPBearer()

@router.get("/secure", dependencies=[Depends(auth)])

auth = HTTPBearer()

@router.get("/secure", dependencies=[Depends(auth)])
def secure_endpoint():
    return {"msg": "seguro"}
