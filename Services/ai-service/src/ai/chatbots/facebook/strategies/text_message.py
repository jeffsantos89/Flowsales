"""
text_message.py
Implements sophisticated text message processing strategy with advanced features.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime
from .base import BaseFacebookStrategy
from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from exceptions import MessageProcessingError

class MessagePriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class MessageContext:
    user_id: str
    text: str
    timestamp: datetime
    session_id: str
    priority: MessagePriority
    metadata: Dict[str, Any]

class TextMessageStrategy(BaseFacebookStrategy):
    """
    Advanced text message processing strategy with support for:
    - Message validation and sanitization
    - Priority handling
    - Context management
    - Structured error handling
    - Performance monitoring
    - Rate limiting
    """

    def __init__(self):
        self.processing_queue = asyncio.Queue()
        self.rate_limit = 100  # messages per minute
        self._last_processed = {}

    def _validate_message(self, payload: Dict[str, Any]) -> None:
        """Validates incoming message payload"""
        required_fields = ["text", "user_id"]
        missing_fields = [field for field in required_fields if not payload.get(field)]
        if missing_fields:
            raise MessageProcessingError(f"Missing required fields: {missing_fields}")

    def _sanitize_text(self, text: str) -> str:
        """Sanitizes input text"""
        return text.strip().replace('\x00', '').lower()

    def _create_context(self, payload: Dict[str, Any]) -> MessageContext:
        """Creates message context with metadata"""
        return MessageContext(
            user_id=payload["user_id"],
            text=self._sanitize_text(payload["text"]),
            timestamp=datetime.now(),
            session_id=payload.get("session_id", ""),
            priority=MessagePriority(payload.get("priority", "medium")),
            metadata=payload.get("metadata", {})
        )

    async def _check_rate_limit(self, user_id: str) -> None:
        """Implements rate limiting per user"""
        current_time = datetime.now()
        if user_id in self._last_processed:
            time_diff = (current_time - self._last_processed[user_id]).total_seconds()
            if time_diff < 60 / self.rate_limit:
                raise MessageProcessingError("Rate limit exceeded")
        self._last_processed[user_id] = current_time

    @retry(max_attempts=3, backoff=2)
    @background_task
    async def process(self, message_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming text messages with advanced error handling and monitoring.
        """
        processing_start = datetime.now()
        try:
            # Validate and prepare message
            self._validate_message(message_payload)
            await self._check_rate_limit(message_payload["user_id"])
            context = self._create_context(message_payload)

            # Log processing start
            logger.info(
                f"[TextMessageStrategy] Processing message from {context.user_id}",
                extra={
                    "user_id": context.user_id,
                    "priority": context.priority.value,
                    "session_id": context.session_id
                }
            )

            # Process message (here you would add your NLP pipeline)
            processed_response = await self._process_message(context)

            # Calculate processing time
            processing_time = (datetime.now() - processing_start).total_seconds()

            return {
                "processed_text": processed_response,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "processing_time": processing_time,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }

        except MessageProcessingError as e:
            logger.warning(
                f"[TextMessageStrategy] Processing error: {str(e)}",
                extra={"error_type": "processing", "user_id": message_payload.get("user_id")}
            )
            return self._create_error_response(e, message_payload)
        except Exception as e:
            logger.exception("[TextMessageStrategy] Unexpected error")
            return self._create_error_response(e, message_payload)

    async def _process_message(self, context: MessageContext) -> str:
        """
        Core message processing logic. 
        Override this method to implement specific NLP pipeline.
        """
        # Add your NLP pipeline here
        return f"Received message: {context.text}"

    def _create_error_response(self, error: Exception, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creates standardized error response"""
        return {
            "error": str(error),
            "error_type": type(error).__name__,
            "user_id": payload.get("user_id", "unknown"),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
