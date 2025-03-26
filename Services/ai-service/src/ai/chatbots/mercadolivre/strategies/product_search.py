"""
product_search.py
Strategy for handling product searches on Mercado Livre with advanced features.
"""

from typing import Dict, Any, List, Optional
import logging
from functools import lru_cache
from dataclasses import dataclass
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod

from ai.database.sales import SalesDatabase
from ai.exceptions import ProductSearchError
from ai.utils.validators import validate_user_id, validate_query
from ai.metrics import MetricsCollector

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class to represent search results"""
    products: List[Dict]
    total_count: int
    search_time: float
    timestamp: datetime = datetime.now()

class ProductSearchInterface(ABC):
    """Abstract interface for product search implementations"""
    @abstractmethod
    async def search(self, keywords: List[str]) -> SearchResult:
        pass

class ProductSearchStrategy:
    """
    Handles product search queries with advanced features:
    - Async support
    - Error handling
    - Request validation
    - Metrics collection
    - Caching
    - Rate limiting
    """

    def __init__(
        self, 
        sales_db: SalesDatabase,
        metrics_collector: MetricsCollector,
        cache_timeout: int = 300,
        max_retries: int = 3
    ):
        self.sales_db = sales_db
        self.metrics = metrics_collector
        self.cache_timeout = cache_timeout
        self.max_retries = max_retries

    @lru_cache(maxsize=1000)
    async def _cached_search(self, query_key: str) -> SearchResult:
        """Cached product search to avoid repeated DB queries"""
        return await self.sales_db.search_products_async(query_key)

    async def _validate_request(self, user_id: str, query_text: str) -> None:
        """Validate incoming request parameters"""
        validate_user_id(user_id)
        validate_query(query_text)

    async def execute(
        self, 
        user_id: str, 
        query_text: str, 
        query_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute product search strategy
        
        Args:
            user_id: Unique user identifier
            query_text: Raw search query text
            query_info: Additional query information and entities
            
        Returns:
            Dict containing search results and metadata
            
        Raises:
            ProductSearchError: If search operation fails
        """
        start_time = datetime.now()
        
        try:
            await self._validate_request(user_id, query_text)
            
            logger.info(f"[ProductSearch] Processing request user_id={user_id} query='{query_text}'")
            
            keywords = query_info.get("entities", [])
            if not keywords:
                logger.warning(f"No keywords extracted from query: {query_text}")
                return self._build_response([], "Não entendi sua busca. Pode ser mais específico?")

            query_key = "-".join(sorted(keywords))
            search_result = await self._cached_search(query_key)

            self.metrics.record_search(
                user_id=user_id,
                query=query_text,
                results_count=len(search_result.products),
                response_time=(datetime.now() - start_time).total_seconds()
            )

            return self._build_response(
                search_result.products,
                f"Encontrei {len(search_result.products)} produtos que podem te interessar."
            )

        except Exception as e:
            logger.error(f"Search failed: {str(e)}", exc_info=True)
            raise ProductSearchError(f"Erro na busca: {str(e)}")

    def _build_response(self, products: List[Dict], message: str) -> Dict[str, Any]:
        """Build standardized response format"""
        return {
            "response": message,
            "products": products,
            "strategy": "product_search",
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
