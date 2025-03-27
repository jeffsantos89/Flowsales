import httpx
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class AuthClientError(Exception):
    """Base exception for AuthClient errors"""
    pass

class AuthClient:
    def __init__(
        self, 
        base_url: str,
        timeout: int = 10,
        max_retries: int = 3,
        verify_ssl: bool = True
    ):
        """
        Initialize AuthClient with configuration parameters
        
        Args:
            base_url: Base URL for the authentication service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def connect(self):
        """Initialize the HTTP client"""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                verify=self.verify_ssl
            )

    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def validate_token(self, token: str) -> Dict[Any, Any]:
        """
        Validate authentication token
        
        Args:
            token: Authentication token to validate
            
        Returns:
            Dict containing validation response
            
        Raises:
            AuthClientError: If validation fails
            httpx.HTTPError: If HTTP request fails
        """
        try:
            if not self._client:
                await self.connect()

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = await self._client.get(
                f"{self.base_url}/validate",
                headers=headers
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            raise AuthClientError(f"Failed to validate token: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AuthClientError(f"Unexpected error during token validation: {str(e)}")

@lru_cache()
def get_auth_client(base_url: str) -> AuthClient:
    """
    Factory function to create cached AuthClient instances
    
    Args:
        base_url: Base URL for the authentication service
        
    Returns:
        AuthClient instance
    """
    return AuthClient(base_url=base_url)
