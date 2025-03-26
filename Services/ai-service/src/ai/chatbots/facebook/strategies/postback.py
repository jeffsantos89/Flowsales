"""
postback.py
Advanced strategy implementation for processing Facebook Messenger postbacks.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from .base import BaseFacebookStrategy
from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from exceptions import PostbackProcessingError, InvalidPayloadError

class PostbackType(Enum):
    """Enumeration of supported postback types"""
    BUTTON = "button"
    MENU = "menu"
    QUICK_REPLY = "quick_reply"
    CUSTOM = "custom"
    UNKNOWN = "unknown"

@dataclass
class PostbackContext:
    """Data class to store postback context information"""
    user_id: str
    timestamp: datetime
    payload: str
    postback_type: PostbackType
    metadata: Dict[str, Any]

class PostbackStrategy(BaseFacebookStrategy):
    """
    Advanced strategy for handling Facebook Messenger postbacks with enhanced
    validation, error handling, and monitoring capabilities.
    """

    def __init__(self):
        super().__init__()
        self.processed_count = 0
        self.error_count = 0

    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate incoming postback payload"""
        required_fields = ["user_id", "postback"]
        return all(field in payload for field in required_fields)

    def determine_postback_type(self, payload: str) -> PostbackType:
        """Determine the type of postback from the payload"""
        try:
            if payload.startswith("button_"):
                return PostbackType.BUTTON
            elif payload.startswith("menu_"):
                return PostbackType.MENU
            elif payload.startswith("qr_"):
                return PostbackType.QUICK_REPLY
            elif payload.startswith("custom_"):
                return PostbackType.CUSTOM
            return PostbackType.UNKNOWN
        except Exception:
            return PostbackType.UNKNOWN

    def create_context(self, message_payload: Dict[str, Any]) -> PostbackContext:
        """Create a context object from the message payload"""
        postback_data = message_payload.get("postback", {})
        payload = postback_data.get("payload", "N/A")
        
        return PostbackContext(
            user_id=message_payload.get("user_id", "unknown"),
            timestamp=datetime.now(),
            payload=payload,
            postback_type=self.determine_postback_type(payload),
            metadata=postback_data.get("metadata", {})
        )

    @retry(max_attempts=3, backoff=2)
    @background_task
    def process(self, message_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the postback with enhanced error handling and monitoring.
        """
        try:
            if not self.validate_payload(message_payload):
                raise InvalidPayloadError("Invalid payload structure")

            context = self.create_context(message_payload)
            logger.info(
                f"[PostbackStrategy] Processing {context.postback_type.value} "
                f"postback from user {context.user_id}"
            )

            # Process the postback based on its type
            result = self._handle_postback(context)
            
            self.processed_count += 1
            return {
                "success": True,
                "postback_payload": context.payload,
                "user_id": context.user_id,
                "type": context.postback_type.value,
                "processed_at": context.timestamp.isoformat(),
                "result": result
            }

        except InvalidPayloadError as e:
            logger.error(f"[PostbackStrategy] Invalid payload: {str(e)}")
            self.error_count += 1
            return self._create_error_response(str(e), message_payload)

        except Exception as e:
            logger.exception("[PostbackStrategy] Unexpected error during postback processing")
            self.error_count += 1
            return self._create_error_response(str(e), message_payload)

    def _handle_postback(self, context: PostbackContext) -> Dict[str, Any]:
        """Handle different types of postbacks"""
        handlers = {
            PostbackType.BUTTON: self._handle_button_postback,
            PostbackType.MENU: self._handle_menu_postback,
            PostbackType.QUICK_REPLY: self._handle_quick_reply_postback,
            PostbackType.CUSTOM: self._handle_custom_postback,
        }
        
        handler = handlers.get(context.postback_type, self._handle_unknown_postback)
        return handler(context)

    def _create_error_response(self, error_message: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "success": False,
            "error": error_message,
            "user_id": payload.get("user_id", "unknown"),
            "timestamp": datetime.now().isoformat()
        }

    # Handler methods for different postback types
    def _handle_button_postback(self, context: PostbackContext) -> Dict[str, Any]:
        return {"action": "button_processed", "payload": context.payload}

    def _handle_menu_postback(self, context: PostbackContext) -> Dict[str, Any]:
        return {"action": "menu_processed", "payload": context.payload}

    def _handle_quick_reply_postback(self, context: PostbackContext) -> Dict[str, Any]:
        return {"action": "quick_reply_processed", "payload": context.payload}

    def _handle_custom_postback(self, context: PostbackContext) -> Dict[str, Any]:
        return {"action": "custom_processed", "payload": context.payload}

    def _handle_unknown_postback(self, context: PostbackContext) -> Dict[str, Any]:
        return {"action": "unknown_processed", "payload": context.payload}

