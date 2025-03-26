from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import asyncio
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    VOICE = "voice"
    LOCATION = "location"
    BUTTON = "button"

@dataclass
class Message:
    content: str
    message_type: MessageType
    metadata: Dict[str, Any]
    timestamp: datetime = datetime.now()

class ChatbotStrategy(ABC):
    """Abstract base class for chatbot strategies"""
    
    @abstractmethod
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming message and return response"""
        pass

    @abstractmethod
    async def handle_error(self, error: Exception) -> Message:
        """Handle errors during message processing"""
        pass

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for implementing retry logic"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

class DefaultStrategy(ChatbotStrategy):
    """Default strategy implementation"""
    
    def __init__(self, fallback_message: str = "I couldn't process your request."):
        self.fallback_message = fallback_message
        self._message_handlers: Dict[MessageType, callable] = self._register_handlers()

    def _register_handlers(self) -> Dict[MessageType, callable]:
        return {
            MessageType.TEXT: self._handle_text,
            MessageType.IMAGE: self._handle_image,
            MessageType.DOCUMENT: self._handle_document,
            MessageType.VOICE: self._handle_voice,
            MessageType.LOCATION: self._handle_location,
            MessageType.BUTTON: self._handle_button
        }

    @retry_on_failure()
    async def process_message(self, message: Message) -> Optional[Message]:
        try:
            handler = self._message_handlers.get(message.message_type)
            if handler:
                return await handler(message)
            return Message(
                content=self.fallback_message,
                message_type=MessageType.TEXT,
                metadata={}
            )
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return await self.handle_error(e)

    async def handle_error(self, error: Exception) -> Message:
        error_message = f"An error occurred: {str(error)}"
        logger.error(error_message)
        return Message(
            content=self.fallback_message,
            message_type=MessageType.TEXT,
            metadata={"error": str(error)}
        )

    async def _handle_text(self, message: Message) -> Message:
        # Implement text message handling logic
        return Message(
            content="Text message received",
            message_type=MessageType.TEXT,
            metadata=message.metadata
        )

    async def _handle_image(self, message: Message) -> Message:
        # Implement image handling logic
        return Message(
            content="Image received",
            message_type=MessageType.TEXT,
            metadata=message.metadata
        )

    async def _handle_document(self, message: Message) -> Message:
        # Implement document handling logic
        return Message(
            content="Document received",
            message_type=MessageType.TEXT,
            metadata=message.metadata
        )

    async def _handle_voice(self, message: Message) -> Message:
        # Implement voice message handling logic
        return Message(
            content="Voice message received",
            message_type=MessageType.TEXT,
            metadata=message.metadata
        )

    async def _handle_location(self, message: Message) -> Message:
        # Implement location handling logic
        return Message(
            content="Location received",
            message_type=MessageType.TEXT,
            metadata=message.metadata
        )

    async def _handle_button(self, message: Message) -> Message:
        # Implement button interaction handling logic
        return Message(
            content="Button interaction received",
            message_type=MessageType.TEXT,
            metadata=message.metadata
        )

class StrategyFactory:
    """Factory class for creating chat strategies"""
    
    _strategies: Dict[str, ChatbotStrategy] = {}

    @classmethod
    def register_strategy(cls, name: str, strategy: ChatbotStrategy) -> None:
        """Register a new strategy"""
        cls._strategies[name] = strategy

    @classmethod
    def get_strategy(cls, name: str) -> ChatbotStrategy:
        """Get a strategy by name"""
        strategy = cls._strategies.get(name)
        if not strategy:
            logger.warning(f"Strategy {name} not found, using default strategy")
            return DefaultStrategy()
        return strategy

    @classmethod
    def list_strategies(cls) -> List[str]:
        """List all registered strategies"""
        return list(cls._strategies.keys())