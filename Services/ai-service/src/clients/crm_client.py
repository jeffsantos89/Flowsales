import httpx
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote
from tenacity import retry, stop_after_attempt, wait_exponential

class CRMClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_lead_by_email(self, email: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/leads?email={email}")
            response.raise_for_status()
            return response.json()

# Exemplo de uso:
# crm_client = CRMClient(base_url="http://crm-service:8000")
logger = logging.getLogger(__name__)

class CRMClientError(Exception):
    """Custom exception for CRM client errors"""
    pass

class CRMClient:
    def __init__(
        self, 
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self._client_config = {
            'timeout': timeout,
            'verify': verify_ssl,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_lead_by_email(self, email: str) -> Dict[str, Any]:
        if not email or '@' not in email:
            raise ValueError("Invalid email format")

        encoded_email = quote(email)
        url = f"{self.base_url}/leads"
        params = {'email': encoded_email}

        try:
            async with httpx.AsyncClient(**self._client_config) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise CRMClientError(f"Failed to fetch lead: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise CRMClientError(f"Unexpected error occurred: {e}")

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(**self._client_config) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False