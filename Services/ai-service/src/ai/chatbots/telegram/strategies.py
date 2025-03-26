from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
import logging
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    VOICE = "voice"
    VIDEO = "video"
    LOCATION = "location"

@dataclass
class Message:
    """Data class to store message information"""
    chat_id: int
    content: Any
    message_type: MessageType
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict] = None

class TelegramStrategy(ABC):
    """Abstract base class for Telegram bot strategies"""
    
    @abstractmethod
    async def process(self, message: Message) -> dict:
        """Process the incoming message and return a response"""
        pass

    @abstractmethod
    def can_handle(self, message: Message) -> bool:
        """Check if the strategy can handle the message type"""
        pass

    def log_operation(self, message: Message, operation: str):
        """Log strategy operations"""
        logger.info(
            f"Strategy: {self.__class__.__name__} | "
            f"Operation: {operation} | "
            f"Chat ID: {message.chat_id} | "
            f"Message Type: {message.message_type}"
        )

class TextMessageStrategy(TelegramStrategy):
    """Handle text messages"""
    
    async def process(self, message: Message) -> dict:
        self.log_operation(message, "processing_text")
        try:
            # Add your text processing logic here
            response = {
                "chat_id": message.chat_id,
                "text": f"Processed text message: {message.content}",
                "type": "text"
            }
            return response
        except Exception as e:
            logger.error(f"Error processing text message: {str(e)}")
            raise

    def can_handle(self, message: Message) -> bool:
        return message.message_type == MessageType.TEXT

class ImageMessageStrategy(TelegramStrategy):
    """Handle image messages"""
    
    async def process(self, message: Message) -> dict:
        self.log_operation(message, "processing_image")
        try:
            # Add your image processing logic here
            response = {
                "chat_id": message.chat_id,
                "text": "Received image message",
                "type": "image"
            }
            return response
        except Exception as e:
            logger.error(f"Error processing image message: {str(e)}")
            raise

    def can_handle(self, message: Message) -> bool:
        return message.message_type == MessageType.IMAGE

class StrategyFactory:
    """Factory for creating appropriate strategy instances"""
    
    def __init__(self):
        self._strategies: Dict[MessageType, TelegramStrategy] = {
            MessageType.TEXT: TextMessageStrategy(),
            MessageType.IMAGE: ImageMessageStrategy(),
        }

    def get_strategy(self, message: Message) -> Optional[TelegramStrategy]:
        """Get the appropriate strategy for the message type"""
        strategy = self._strategies.get(message.message_type)
        if not strategy:
            logger.warning(f"No strategy found for message type: {message.message_type}")
        return strategy

class TelegramMessageHandler:
    """Main handler for processing Telegram messages"""
    
    def __init__(self):
        self.strategy_factory = StrategyFactory()

    async def handle_message(self, message: Message) -> dict:
        """Handle incoming messages using appropriate strategy"""
        try:
            strategy = self.strategy_factory.get_strategy(message)
            if not strategy:
                return {
                    "chat_id": message.chat_id,
                    "text": "Unsupported message type",
                    "type": "error"
                }

            if not strategy.can_handle(message):
                return {
                    "chat_id": message.chat_id,
                    "text": "Cannot handle this message type",
                    "type": "error"
                }

            return await strategy.process(message)

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return {
                "chat_id": message.chat_id,
                "text": "An error occurred while processing your message",
                "type": "error"
            }