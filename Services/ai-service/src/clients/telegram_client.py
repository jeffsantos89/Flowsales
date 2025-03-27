import logging
from typing import Optional, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class TelegramClientError(Exception):
    """Custom exception for TelegramClient errors"""
    pass

class TelegramClient:
    def __init__(
        self, 
        base_url: str,
        bot_token: str,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize TelegramClient with configuration parameters.
        
        Args:
            base_url: Base URL for Telegram API
            bot_token: Telegram Bot Token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.bot_token = bot_token
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> 'TelegramClient':
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False
    ) -> Dict[str, Any]:
        """
        Send a message through Telegram API.
        
        Args:
            chat_id: Recipient's chat ID
            text: Message text
            parse_mode: Message parse mode (HTML, Markdown, etc.)
            disable_notification: Whether to send message silently
            
        Returns:
            Dict containing API response
            
        Raises:
            TelegramClientError: If the API request fails
        """
        try:
            if not self._client:
                self._client = httpx.AsyncClient(timeout=self.timeout)

            payload = {
                "chat_id": chat_id,
                "text": text,
                "disable_notification": disable_notification
            }
            
            if parse_mode:
                payload["parse_mode"] = parse_mode

            response = await self._client.post(
                f"{self.base_url}/bot{self.bot_token}/sendMessage",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Telegram API error: {str(e)}")
            raise TelegramClientError(f"Failed to send message: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise TelegramClientError(f"Unexpected error: {str(e)}")

    async def close(self):
        """Close the HTTP client connection"""
        if self._client:
            await self._client.aclose()
