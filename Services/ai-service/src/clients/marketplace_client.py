import httpx
from typing import Dict, Any, Optional
import logging
from functools import wraps
import asyncio
from datetime import timedelta

logger = logging.getLogger(__name__)

class MarketplaceClientError(Exception):
    """Custom exception for MarketplaceClient errors"""
    pass

class MarketplaceClient:
    def __init__(
        self, 
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        """Initialize the HTTP client"""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": "MarketplaceClient/1.0",
                    "Content-Type": "application/json"
                }
            )

    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Generic method to make HTTP requests with retry logic"""
        if not self._client:
            await self.connect()

        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                if attempt == self.max_retries - 1:
                    raise MarketplaceClientError(f"Request failed after {self.max_retries} attempts: {str(e)}")
            
            except httpx.RequestError as e:
                logger.error(f"Request error occurred: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise MarketplaceClientError(f"Network error after {self.max_retries} attempts: {str(e)}")
            
            await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

    async def get_product_info(self, product_id: str) -> Dict[str, Any]:
        """Get product information by ID"""
        return await self._make_request(
            method="GET",
            endpoint=f"/products/{product_id}"
        )

    async def update_stock(self, product_id: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update product stock information"""
        return await self._make_request(
            method="PUT",
            endpoint=f"/products/{product_id}/stock",
            json=stock_data
        )

