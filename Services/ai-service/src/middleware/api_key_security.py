import hashlib
from datetime import datetime
from typing import Optional, Dict
from fastapi import Request, HTTPException
from pydantic import BaseModel
import logging
from functools import lru_cache
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIKey(BaseModel):
    key: str
    client_id: str
    is_active: bool
    rate_limit: int  # requisições por minuto
    last_used: datetime
    usage_count: int

class APIKeyManager:
    def __init__(self):
        self._api_keys: Dict[str, APIKey] = {}
        self._load_api_keys()

    def _load_api_keys(self) -> None:
        """Carrega as chaves de API do ambiente ou banco de dados"""
        # Exemplo usando variáveis de ambiente
        default_key = os.getenv("DEFAULT_API_KEY")
        if default_key:
            self._api_keys[default_key] = APIKey(
                key=default_key,
                client_id="default",
                is_active=True,
                rate_limit=100,
                last_used=datetime.now(),
                usage_count=0
            )

    @lru_cache(maxsize=1000)
    def _hash_key(self, key: str) -> str:
        """Gera hash da chave para comparação segura"""
        return hashlib.sha256(key.encode()).hexdigest()

    def validate_key(self, api_key: str) -> Optional[APIKey]:
        """Valida a chave de API e atualiza métricas de uso"""
        if not api_key:
            return None

        key_data = self._api_keys.get(api_key)
        if not key_data or not key_data.is_active:
            return None

        # Verifica rate limit
        current_time = datetime.now()
        time_diff = (current_time - key_data.last_used).total_seconds()
        if time_diff < 60 and key_data.usage_count >= key_data.rate_limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

        # Atualiza métricas
        key_data.last_used = current_time
        key_data.usage_count = 0 if time_diff >= 60 else key_data.usage_count + 1
        
        return key_data

api_key_manager = APIKeyManager()

async def verify_api_key(request: Request):
    """Middleware para autenticação via API Key"""
    try:
        api_key = request.headers.get("X-API-Key")
        client_ip = request.client.host
        
        key_data = api_key_manager.validate_key(api_key)
        if not key_data:
            logger.warning(f"Tentativa de acesso inválida - IP: {client_ip}")
            raise HTTPException(
                status_code=403,
                detail="Invalid or unauthorized API Key"
            )

        # Adiciona informações do cliente ao request para uso posterior
        request.state.client_id = key_data.client_id
        request.state.api_key_data = key_data

        logger.info(f"Acesso autorizado - Client ID: {key_data.client_id}, IP: {client_ip}")

    except Exception as e:
        logger.error(f"Erro na verificação da API Key: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during API key verification"
        )
