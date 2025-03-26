from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime
import aiohttp
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from urllib.parse import urlencode
from contextlib import asynccontextmanager
from enum import Enum, auto
import backoff
from cachetools import TTLCache
from aiohttp import ClientTimeout, TCPConnector
from nlp import HuggingFaceProcessor

# Configuração avançada de logging com correlation ID
class CorrelationIDFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = 'undefined'
        return True

logger = logging.getLogger(__name__)
logger.addFilter(CorrelationIDFilter())
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] %(message)s'
)

class MLIntent(Enum):
    """Enumeração aprimorada de intents do ML"""
    PRODUCT_INFO = auto()
    PRICE_COMPARISON = auto()
    SHIPPING_INQUIRY = auto()
    RETURNS = auto()
    NEGOTIATE_PRICE = auto()
    CHECK_STOCK = auto()
    UNKNOWN = auto()
    ERROR = auto()

    @classmethod
    def from_str(cls, value: str) -> 'MLIntent':
        try:
            return cls[value.upper()]
        except KeyError:
            return cls.UNKNOWN

@dataclass(frozen=True)
class QueryConfig:
    """Configuração imutável para queries do MercadoLivre"""
    base_url: str = "https://api.mercadolibre.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    cache_ttl: int = 300
    batch_size: int = 50
    rate_limit: int = 100
    correlation_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"))
    max_connections: int = 100
    connection_timeout: int = 10

class MLQueryException(Exception):
    """Exceção customizada com mais informações"""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class QueryBuilder:
    """Builder pattern aprimorado para queries"""
    def __init__(self):
        self._params: Dict[str, Any] = {}
        self._filters: Dict[str, Union[str, List[str]]] = {}
        self._sort: Optional[str] = None
        self._order: Optional[str] = None

    def add_param(self, key: str, value: Any) -> 'QueryBuilder':
        self._params[key] = str(value)
        return self

    def add_filter(self, key: str, value: Union[str, List[str]]) -> 'QueryBuilder':
        self._filters[key] = value
        return self

    def add_sort(self, field: str, ascending: bool = True) -> 'QueryBuilder':
        self._sort = field
        self._order = "asc" if ascending else "desc"
        return self

    def build(self) -> str:
        query_params = {**self._params}
        if self._filters:
            query_params['filters'] = self._filters
        if self._sort:
            query_params['sort'] = self._sort
            query_params['order'] = self._order
        return urlencode(query_params)

class MLQuery:
    """Implementação robusta do handler de queries do MercadoLivre"""
    def __init__(self, config: Optional[QueryConfig] = None):
        self.config = config or QueryConfig()
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache = TTLCache(maxsize=1000, ttl=self.config.cache_ttl)
        self._rate_limiter = asyncio.Semaphore(self.config.rate_limit)
        self._connector = TCPConnector(limit=self.config.max_connections)

    @asynccontextmanager
    async def _get_session(self):
        if not self._session:
            timeout = ClientTimeout(
                total=self.config.timeout,
                connect=self.config.connection_timeout
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=self._connector
            )
        try:
            yield self._session
        finally:
            if self._session and not self._session.closed:
                await self._session.close()

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError, MLQueryException),
        max_tries=3,
        giveup=lambda e: isinstance(e, MLQueryException) and e.status_code in {400, 401, 403}
    )
    async def _make_request(self, url: str) -> Dict:
        async with self._rate_limiter:
            if url in self._cache:
                logger.debug(f"Cache hit for URL: {url}")
                return self._cache[url]

            async with self._get_session() as session:
                async with session.get(url) as response:
                    content = await response.text()
                    
                    if response.status == 200:
                        data = await response.json()
                        self._cache[url] = data
                        return data
                    
                    error_details = {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'content': content
                    }
                    
                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', self.config.retry_delay))
                        await asyncio.sleep(retry_after)
                        raise MLQueryException("Rate limit exceeded", response.status, error_details)
                    
                    raise MLQueryException(
                        f"Query failed: {content}",
                        response.status,
                        error_details
                    )

    async def execute_query(self, endpoint: str, params: Dict) -> Dict:
        url = f"{self.config.base_url}{endpoint}"
        query_string = QueryBuilder().add_param(**params).build()
        full_url = f"{url}?{query_string}"
        
        logger.info(
            "Executing query",
            extra={
                'correlation_id': self.config.correlation_id,
                'url': full_url
            }
        )
        
        try:
            return await self._make_request(full_url)
        except Exception as e:
            logger.error(
                f"Query failed: {str(e)}",
                extra={'correlation_id': self.config.correlation_id},
                exc_info=True
            )
            raise

    # Métodos específicos de busca melhorados
    async def search_products(self, query: str, limit: int = 50, sort_by: str = None) -> Dict:
        builder = QueryBuilder()\
            .add_param("q", query)\
            .add_param("limit", min(limit, self.config.batch_size))
            
        if sort_by:
            builder.add_sort(sort_by)
            
        return await self.execute_query("/sites/MLB/search", builder._params)

    async def get_product_details(self, product_id: str) -> Dict:
        return await self.execute_query(f"/items/{product_id}", {})

class MercadoLibreQueryPipeline:
    """Pipeline NLP aprimorado com análise de sentimento"""
    def __init__(self, nlp_processor: HuggingFaceProcessor):
        self.nlp_processor = nlp_processor
        self._cache = TTLCache(maxsize=1000, ttl=3600)

    async def process(self, text: str) -> Dict[str, Any]:
        cache_key = hash(text.strip().lower())
        
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            cleaned = self._clean_text(text)
            nlp_result = await self.nlp_processor.analyze(cleaned)
            
            result = {
                "intent": self._determine_intent(cleaned, nlp_result),
                "entities": nlp_result.get("entities", []),
                "sentiment": nlp_result.get("sentiment", "neutral"),
                "confidence": nlp_result.get("confidence", 0.0),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            self._cache[cache_key] = result
            return result
        except Exception as e:
            logger.exception("NLP processing error")
            return {
                "intent": MLIntent.ERROR.value,
                "entities": [],
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat()
            }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Limpeza e normalização de texto aprimorada"""
        return " ".join(text.strip().lower().split())

    def _determine_intent(self, cleaned_text: str, nlp_result: Dict) -> str:
        """Determinação sofisticada de intent com regras de negócio"""
        intent_rules = {
            MLIntent.NEGOTIATE_PRICE: lambda t: any(word in t for word in ["desconto", "negociar", "melhor preço"]),
            MLIntent.CHECK_STOCK: lambda t: any(word in t for word in ["estoque", "quantidade", "disponível"]),
            MLIntent.SHIPPING_INQUIRY: lambda t: any(word in t for word in ["envio", "frete", "entrega"]),
            MLIntent.RETURNS: lambda t: any(word in t for word in ["devolução", "troca", "garantia"])
        }

        for intent, rule in intent_rules.items():
            if rule(cleaned_text):
                return intent.value

        return MLIntent[nlp_result.get("intent", "UNKNOWN")].value
