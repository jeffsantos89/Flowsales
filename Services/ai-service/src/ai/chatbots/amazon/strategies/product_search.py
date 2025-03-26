"""
product_search.py
Amazon product search strategy with advanced error handling, monitoring, and scalability.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import httpx
from datetime import datetime
from abc import ABC, abstractmethod
import uuid
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager

from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from utils.cache import TTLCache
from .base import BaseAmazonStrategy

class SearchError(Exception):
    """Base exception for search related errors."""
    pass

class APIError(SearchError):
    """API related errors."""
    pass

class ValidationError(SearchError):
    """Input validation errors."""
    pass

class SearchStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SearchMetrics:
    """Metrics for search operations."""
    request_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    cache_hit: bool = False
    error: Optional[str] = None

@dataclass
class SearchRequest:
    """Validated search request data."""
    query: str
    max_results: int
    filters: Dict[str, Any]
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> 'SearchRequest':
        """Factory method to create SearchRequest from raw payload."""
        if not payload.get("query"):
            raise ValidationError("Query parameter is required")
            
        return cls(
            query=payload["query"],
            max_results=min(int(payload.get("max_results", 5)), 100),
            filters=payload.get("filters", {})
        )

class ProductSearchStrategy(BaseAmazonStrategy):
    """Enhanced Amazon product search strategy with monitoring and scalability features."""
    
    def __init__(
        self, 
        cache: Optional[TTLCache] = None,
        api_endpoint: Optional[str] = None,
        max_concurrent_requests: int = 10
    ):
        self.cache = cache or TTLCache()
        self.api_endpoint = api_endpoint or "https://api.amazon.fake/v1/search"
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._metrics: Dict[str, SearchMetrics] = {}

    @asynccontextmanager
    async def _api_client(self):
        """Context manager for API client with timeout and retry configuration."""
        async with httpx.AsyncClient(
            timeout=15,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            headers=self._get_default_headers()
        ) as client:
            yield client

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "User-Agent": "ProductSearchBot/1.0",
            "Accept": "application/json",
            "X-Request-ID": str(uuid.uuid4())
        }

    @retry(max_attempts=3, backoff=2)
    @background_task
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute product search with enhanced monitoring and error handling.
        """
        request_id = str(uuid.uuid4())
        metrics = SearchMetrics(
            request_id=request_id,
            start_time=datetime.utcnow()
        )
        
        try:
            search_request = SearchRequest.from_payload(payload)
            return await self._process_search_request(search_request, metrics)
        except Exception as e:
            logger.exception("[ProductSearchStrategy] Search operation failed")
            metrics.error = str(e)
            raise
        finally:
            metrics.end_time = datetime.utcnow()
            metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            self._metrics[request_id] = metrics

    async def _process_search_request(
        self, 
        search_request: SearchRequest,
        metrics: SearchMetrics
    ) -> Dict[str, Any]:
        """Process validated search request."""
        cache_key = self._generate_cache_key(search_request)
        
        # Check cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            metrics.cache_hit = True
            return cached_result

        async with self._semaphore:
            products = await self._fetch_products_from_api(search_request)
            
        result = {
            "request_id": metrics.request_id,
            "results": products,
            "query": search_request.query,
            "count": len(products),
            "filters_applied": search_request.filters,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.cache.set(cache_key, result)
        return result

    def _generate_cache_key(self, search_request: SearchRequest) -> str:
        """Generate unique cache key based on search parameters."""
        return f"product_search::{search_request.query}::{search_request.max_results}::{hash(frozenset(search_request.filters.items()))}"

    async def _fetch_products_from_api(
        self, 
        search_request: SearchRequest
    ) -> List[Dict[str, Any]]:
        """Fetch products from API with enhanced error handling."""
        async with self._api_client() as client:
            try:
                params = {
                    "q": search_request.query,
                    "limit": search_request.max_results,
                    **search_request.filters
                }
                
                resp = await client.get(self.api_endpoint, params=params)
                resp.raise_for_status()
                
                data = resp.json()
                return data.get("items", [])
            
            except httpx.HTTPStatusError as e:
                raise APIError(f"API request failed with status {e.response.status_code}")
            except httpx.RequestError as e:
                raise APIError(f"API request failed: {str(e)}")

    def get_metrics(self) -> Dict[str, SearchMetrics]:
        """Get search operation metrics."""
        return self._metrics
