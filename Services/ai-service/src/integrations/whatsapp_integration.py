import requests
import os
import logging
from typing import Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppMessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"

@dataclass
class WhatsAppConfig:
    api_url: str = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v15.0")
    access_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN")
    max_retries: int = 3
    timeout: int = 10

class WhatsAppAPIException(Exception):
    """Custom exception for WhatsApp API errors"""
    pass

class WhatsAppClient:
    def __init__(self, config: Optional[WhatsAppConfig] = None):
        self.config = config or WhatsAppConfig()
        if not self.config.access_token:
            raise ValueError("WhatsApp access token is required")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def send_message(
        self,
        recipient: str,
        message: Union[str, Dict],
        message_type: WhatsAppMessageType = WhatsAppMessageType.TEXT
    ) -> Dict:
        """
        Send a WhatsApp message with retry mechanism and error handling
        
        Args:
            recipient: The recipient's phone number
            message: The message content (str for text, dict for media)
            message_type: Type of message to send (text, image, etc.)
        
        Returns:
            Dict: API response
            
        Raises:
            WhatsAppAPIException: If the API request fails
        """
        try:
            url = f"{self.config.api_url}/me/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": message_type.value,
            }

            # Handle different message types
            if message_type == WhatsAppMessageType.TEXT:
                payload[message_type.value] = {"body": message}
            else:
                payload[message_type.value] = message

            logger.info(f"Sending WhatsApp message to {recipient}")
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.info(f"Message sent successfully to {recipient}")
            return response_data

        except RequestException as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            raise WhatsAppAPIException(f"WhatsApp API error: {str(e)}")

# Usage example
if __name__ == "__main__":
    client = WhatsAppClient()
    
    # Send text message
    client.send_message(
        recipient="1234567890",
        message="Hello, this is a test message!"
    )
    
    # Send image message
    client.send_message(
        recipient="1234567890",
        message={"link": "https://example.com/image.jpg"},
        message_type=WhatsAppMessageType.IMAGE
    )
