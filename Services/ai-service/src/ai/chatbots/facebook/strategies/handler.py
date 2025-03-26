"""
handler.py
Unified strategy for handling different types of Facebook messages (text, quick reply, postback)
with enhanced error handling and extensibility.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from utils.logger import logger


@dataclass
class MessageContext:
    """Data class to hold message context and metadata"""
    raw_payload: Dict[str, Any]
    sender_id: str
    timestamp: int
    message_type: str


class MessageType(Enum):
    """Enum for supported message types"""
    TEXT = "text"
    QUICK_REPLY = "quick_reply"
    POSTBACK = "postback"
    UNKNOWN = "unknown"


class MessageProcessingError(Exception):
    """Custom exception for message processing errors"""
    pass


class IMessageStrategy(ABC):
    """Abstract base class for message strategies"""
    @abstractmethod
    def process(self, context: MessageContext) -> Dict[str, Any]:
        pass

    @abstractmethod
    def can_handle(self, payload: Dict[str, Any]) -> bool:
        pass


class TextMessageStrategy(IMessageStrategy):
    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "text" in payload and not payload.get("quick_reply")

    def process(self, context: MessageContext) -> Dict[str, Any]:
        # Implement text message handling logic
        pass


class QuickReplyStrategy(IMessageStrategy):
    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "quick_reply" in payload

    def process(self, context: MessageContext) -> Dict[str, Any]:
        # Implement quick reply handling logic
        pass


class PostbackStrategy(IMessageStrategy):
    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "postback" in payload

    def process(self, context: MessageContext) -> Dict[str, Any]:
        # Implement postback handling logic
        pass


class FacebookMessageHandler:
    """
    Enhanced message handler with improved error handling, logging, and extensibility.
    """

    def __init__(self):
        self._strategies: Dict[MessageType, IMessageStrategy] = {
            MessageType.TEXT: TextMessageStrategy(),
            MessageType.QUICK_REPLY: QuickReplyStrategy(),
            MessageType.POSTBACK: PostbackStrategy(),
        }

    def _create_message_context(self, payload: Dict[str, Any]) -> MessageContext:
        """Create a message context from the raw payload"""
        return MessageContext(
            raw_payload=payload,
            sender_id=payload.get("sender", {}).get("id", "unknown"),
            timestamp=payload.get("timestamp", 0),
            message_type=self._determine_message_type(payload)
        )

    def _determine_message_type(self, payload: Dict[str, Any]) -> str:
        """Determine the type of message from the payload"""
        for strategy in self._strategies.values():
            if strategy.can_handle(payload):
                return strategy.__class__.__name__
        return MessageType.UNKNOWN.value

    def _get_strategy(self, payload: Dict[str, Any]) -> Optional[IMessageStrategy]:
        """Get the appropriate strategy for the message type"""
        for strategy in self._strategies.values():
            if strategy.can_handle(payload):
                return strategy
        return None

    async def handle_incoming(self, message_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message with enhanced error handling and logging
        """
        try:
            context = self._create_message_context(message_payload)
            logger.info(f"Processing message type: {context.message_type} from sender: {context.sender_id}")

            strategy = self._get_strategy(message_payload)
            if not strategy:
                raise MessageProcessingError("Unsupported message type")

            response = await strategy.process(context)
            logger.info(f"Successfully processed message from sender: {context.sender_id}")
            return response

        except MessageProcessingError as e:
            logger.warning(f"Message processing error: {str(e)}")
            return {"error": str(e), "error_type": "message_processing"}

        except Exception as e:
            logger.exception("Unexpected error in message handling")
            return {
                "error": "An unexpected error occurred",
                "error_type": "internal_error",
                "error_details": str(e)
            }

    def register_strategy(self, message_type: MessageType, strategy: IMessageStrategy) -> None:
        """Register a new message handling strategy"""
        self._strategies[message_type] = strategy
