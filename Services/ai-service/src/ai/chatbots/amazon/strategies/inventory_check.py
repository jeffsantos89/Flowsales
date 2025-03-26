"""
inventory_check.py
Estratégia para verificar disponibilidade de estoque com recursos avançados de resiliência,
monitoramento e otimização de performance.
"""

from typing import Dict, Any, Optional, Union
import asyncio
from datetime import datetime
import httpx
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from prometheus_client import Counter, Histogram

from utils.logger import logger
from ai.decorators.background_task import background_task
from utils.cache import TTLCache
from config import settings
from .base import BaseAmazonStrategy

# Métricas para monitoramento
INVENTORY_REQUESTS = Counter(
    'inventory_requests_total',
    'Total de requisições ao serviço de inventário',
    ['status']
)
INVENTORY_LATENCY = Histogram(
    'inventory_request_latency_seconds',
    'Latência das requisições ao serviço de inventário'
)

class InventoryResponse(BaseModel):
    """Schema de validação para resposta da API"""
    in_stock: bool
    quantity: int
    product_id: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="available")

class InventoryCheckStrategy(BaseAmazonStrategy):
    def __init__(
        self,
        cache: Optional[TTLCache] = None,
        timeout: int = 15,
        cache_ttl: int = 300
    ):
        self.cache = cache or TTLCache(default_ttl=cache_ttl)
        self.timeout = timeout
        self.api_endpoint = settings.AMAZON_INVENTORY_API_ENDPOINT
        self._session: Optional[httpx.AsyncClient] = None

    async def _get_session(self) -> httpx.AsyncClient:
        """Lazy initialization do cliente HTTP"""
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=40),
                headers={"User-Agent": settings.USER_AGENT}
            )
        return self._session

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    @background_task
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa verificação de estoque com suporte a cache e métricas.
        
        Args:
            payload: Dict contendo product_id
        Returns:
            Dict com informações de estoque validadas
        Raises:
            ValueError: Se payload estiver inválido
            RetryError: Se todas as tentativas falharem
        """
        try:
            product_id = self._validate_payload(payload)
            cache_key = f"inventory_check::{product_id}"

            # Tenta recuperar do cache
            if cached := await self._get_cached_data(cache_key):
                INVENTORY_REQUESTS.labels(status="cache_hit").inc()
                return cached

            # Busca dados frescos
            with INVENTORY_LATENCY.time():
                data = await self._fetch_inventory(product_id)

            # Valida e processa resposta
            inventory_data = InventoryResponse(**data).dict()
            await self._update_cache(cache_key, inventory_data)

            INVENTORY_REQUESTS.labels(status="success").inc()
            return inventory_data

        except Exception as e:
            INVENTORY_REQUESTS.labels(status="error").inc()
            logger.exception("[InventoryCheckStrategy] Erro crítico: %s", str(e))
            raise

    def _validate_payload(self, payload: Dict[str, Any]) -> str:
        """Valida payload da requisição"""
        if not (product_id := payload.get("product_id")):
            raise ValueError("product_id é obrigatório")
        return product_id

    async def _get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera dados do cache de forma assíncrona"""
        if cached := self.cache.get(key):
            logger.info("[InventoryCheckStrategy] Cache hit para %s", key)
            return cached
        return None

    async def _update_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Atualiza cache de forma assíncrona"""
        self.cache.set(key, data)
        logger.info("[InventoryCheckStrategy] Cache atualizado para %s", key)

    async def _fetch_inventory(self, product_id: str) -> Dict[str, Any]:
        """Busca dados de inventário na API"""
        session = await self._get_session()
        try:
            resp = await session.get(
                self.api_endpoint,
                params={"product_id": product_id}
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            logger.error("[InventoryCheckStrategy] Erro HTTP: %s", str(e))
            raise

    async def cleanup(self):
        """Cleanup de recursos"""
        if self._session and not self._session.is_closed:
            await self._session.aclose()
