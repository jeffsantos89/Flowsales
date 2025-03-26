from typing import Dict, List, Optional, Union
from urllib.parse import urlparse
import requests
import logging
import json
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebhookManager")

class WebhookException(Exception):
    """Exceção base para operações com webhooks"""
    pass

class WebhookStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

@dataclass
class WebhookConfig:
    """Configuração de um webhook"""
    id: str
    url: str
    status: WebhookStatus
    created_at: datetime
    last_called: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 5

class WebhookManager:
    """
    Gerenciador de webhooks com suporte a validação, retry, logging e monitoramento
    """
    def __init__(self, base_url: str = "https://webhook-service.com"):
        self.base_url = base_url
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WebhookManager/1.0",
            "Content-Type": "application/json"
        })

    def validate_url(self, url: str) -> bool:
        """Valida uma URL de webhook"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme in ["http", "https"]:
                raise ValueError("URL deve usar protocolo HTTP(S)")
            if not parsed.netloc:
                raise ValueError("URL deve conter um host válido")
            
            response = self.session.head(url, timeout=5)
            if response.status_code not in [200, 201, 202]:
                raise ValueError(f"URL retornou status code inválido: {response.status_code}")
            
            return True
        except Exception as e:
            logger.warning(f"Validação de URL falhou: {url} | {str(e)}")
            raise WebhookException(f"URL inválida: {str(e)}")

    def register(self, webhook_id: str, url: str) -> WebhookConfig:
        """Registra um novo webhook"""
        if webhook_id in self.webhooks:
            raise WebhookException(f"Webhook '{webhook_id}' já existe")
        
        if self.validate_url(url):
            webhook = WebhookConfig(
                id=webhook_id,
                url=url,
                status=WebhookStatus.ACTIVE,
                created_at=datetime.utcnow()
            )
            self.webhooks[webhook_id] = webhook
            logger.info(f"Webhook registrado: {webhook_id} => {url}")
            return webhook

    def unregister(self, webhook_id: str) -> None:
        """Remove um webhook registrado"""
        if webhook_id not in self.webhooks:
            raise WebhookException(f"Webhook '{webhook_id}' não encontrado")
        
        webhook = self.webhooks.pop(webhook_id)
        logger.info(f"Webhook removido: {webhook_id}")
        return webhook

    def list_webhooks(self) -> List[Dict[str, Union[str, datetime]]]:
        """Lista todos os webhooks registrados"""
        return [
            {
                "id": webhook.id,
                "url": webhook.url,
                "status": webhook.status.value,
                "created_at": webhook.created_at.isoformat(),
                "last_called": webhook.last_called.isoformat() if webhook.last_called else None,
                "retry_count": webhook.retry_count
            }
            for webhook in self.webhooks.values()
        ]

    async def send_event(self, webhook_id: str, payload: Dict, retry: bool = True) -> Dict:
        """Envia evento para um webhook com suporte a retry"""
        if webhook_id not in self.webhooks:
            raise WebhookException(f"Webhook '{webhook_id}' não encontrado")

        webhook = self.webhooks[webhook_id]
        
        try:
            response = self.session.post(
                webhook.url,
                json=payload,
                timeout=webhook.timeout
            )
            response.raise_for_status()
            
            webhook.last_called = datetime.utcnow()
            webhook.status = WebhookStatus.ACTIVE
            webhook.retry_count = 0
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text
            }
            
        except requests.RequestException as e:
            webhook.retry_count += 1
            if retry and webhook.retry_count <= webhook.max_retries:
                logger.warning(f"Retry {webhook.retry_count}/{webhook.max_retries} para {webhook_id}")
                return await self.send_event(webhook_id, payload, retry)
            
            webhook.status = WebhookStatus.ERROR
            logger.error(f"Falha ao enviar evento para {webhook_id}: {str(e)}")
            raise WebhookException(f"Erro ao enviar evento: {str(e)}")

    def health_check(self) -> Dict[str, int]:
        """Retorna métricas sobre o estado dos webhooks"""
        stats = {status: 0 for status in WebhookStatus}
        for webhook in self.webhooks.values():
            stats[webhook.status] += 1
        return {k.value: v for k, v in stats.items()}
