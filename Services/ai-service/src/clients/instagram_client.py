from typing import Dict, Any, Optional
import httpx
from httpx import Response
import logging
import asyncio
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)

class InstagramClientError(Exception):
    """Custom exception for Instagram client errors"""
    pass

def retry_on_failure(retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except httpx.HTTPError as e:
                    if attempt == retries - 1:
                        raise InstagramClientError(f"Failed after {retries} attempts: {str(e)}")
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                    await asyncio.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

class InstagramClient:
    def __init__(
        self, 
        base_url: str,
        timeout: float = 10.0,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = headers or {}
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Response:
        if not self.client:
            raise InstagramClientError("Client not initialized. Use async with context manager.")
        
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            raise InstagramClientError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise InstagramClientError(f"Unexpected error: {str(e)}")

    @retry_on_failure()
    async def post_comment(self, post_id: str, message: str) -> Dict[str, Any]:
        """
        Post a comment on an Instagram post
        
        Args:
            post_id: The ID of the post
            message: The comment message
            
        Returns:
            Dict containing the response data
        """
        endpoint = f"/posts/{post_id}/comments"
        response = await self._make_request(
            "POST",
            endpoint,
            json={"message": message}
        )
        return response.json()

    @retry_on_failure()
    async def get_comments(self, post_id: str) -> Dict[str, Any]:
        """
        Get comments from an Instagram post
        
        Args:
            post_id: The ID of the post
            
        Returns:
            Dict containing the comments data
        """
        endpoint = f"/posts/{post_id}/comments"
        response = await self._make_request("GET", endpoint)
        return response.json()

