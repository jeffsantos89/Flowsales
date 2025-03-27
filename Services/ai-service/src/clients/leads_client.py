import httpx
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LeadsClientException(Exception):
    """Custom exception for LeadsClient errors"""
    pass

class LeadsClient:
    def __init__(
        self, 
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = headers or {}
        self._client: Optional[httpx.AsyncClient] = None

    @asynccontextmanager
    async def get_client(self):
        """Context manager for handling client lifecycle"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers
            )
        try:
            yield self._client
        finally:
            if self._client:
                await self._client.aclose()
                self._client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generic method to make HTTP requests with error handling"""
        try:
            async with self.get_client() as client:
                url = f"{self.base_url}{endpoint}"
                logger.debug(f"Making {method} request to {url}")
                
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"Timeout error while {method} {endpoint}")
            raise LeadsClientException("Request timed out")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} while {method} {endpoint}")
            raise LeadsClientException(f"HTTP {e.response.status_code}: {e.response.text}")
            
        except Exception as e:
            logger.error(f"Unexpected error while {method} {endpoint}: {str(e)}")
            raise LeadsClientException(f"Unexpected error: {str(e)}")

    async def get_lead_by_id(self, lead_id: str) -> Dict[str, Any]:
        """Retrieve a lead by its ID"""
        return await self._make_request("GET", f"/leads/{lead_id}")

    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead"""
        return await self._make_request("POST", "/leads", json=lead_data)

