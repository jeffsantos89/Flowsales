from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    QUESTION = "question"
    COMPLAINT = "complaint"
    ORDER_STATUS = "order_status"
    PRODUCT_INFO = "product_info"
    PRICE_INQUIRY = "price_inquiry"
    OTHER = "other"

@dataclass
class Message:
    content: str
    sender_id: str
    timestamp: datetime
    message_type: MessageType
    metadata: Dict[str, Any] = None

class ResponseStrategy(ABC):
    @abstractmethod
    async def process(self, message: Message) -> str:
        """Process the incoming message and return appropriate response"""
        pass

    def _validate_message(self, message: Message) -> bool:
        """Validate incoming message"""
        return bool(message.content and message.sender_id)

    def _log_interaction(self, message: Message, response: str):
        """Log interaction for monitoring and analytics"""
        logger.info(
            f"Interaction - Sender: {message.sender_id}, "
            f"Type: {message.message_type.value}, "
            f"Message: {message.content[:50]}..."
        )

class ProductInquiryStrategy(ResponseStrategy):
    async def process(self, message: Message) -> str:
        if not self._validate_message(message):
            return "Invalid message format"
        
        # Add your product inquiry logic here
        response = "Thank you for your product inquiry. Our team will assist you shortly."
        self._log_interaction(message, response)
        return response

class OrderStatusStrategy(ResponseStrategy):
    async def process(self, message: Message) -> str:
        if not self._validate_message(message):
            return "Invalid message format"
        
        # Add your order status logic here
        response = "We're checking your order status. Please wait a moment."
        self._log_interaction(message, response)
        return response

class ComplaintHandlingStrategy(ResponseStrategy):
    async def process(self, message: Message) -> str:
        if not self._validate_message(message):
            return "Invalid message format"
        
        # Add your complaint handling logic here
        response = "We apologize for any inconvenience. Your complaint has been registered."
        self._log_interaction(message, response)
        return response

class StrategyFactory:
    _strategies: Dict[MessageType, ResponseStrategy] = {
        MessageType.PRODUCT_INFO: ProductInquiryStrategy(),
        MessageType.ORDER_STATUS: OrderStatusStrategy(),
        MessageType.COMPLAINT: ComplaintHandlingStrategy(),
    }

    @classmethod
    def get_strategy(cls, message_type: MessageType) -> ResponseStrategy:
        """Get appropriate strategy based on message type"""
        return cls._strategies.get(message_type, DefaultStrategy())

class DefaultStrategy(ResponseStrategy):
    async def process(self, message: Message) -> str:
        response = "I'm sorry, I couldn't understand your request. Please try to rephrase it."
        self._log_interaction(message, response)
        return response

class MercadoLivreMessageHandler:
    def __init__(self):
        self.strategy_factory = StrategyFactory()

    async def handle_message(self, content: str, sender_id: str, 
                           message_type: MessageType, 
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Main entry point for handling messages
        """
        try:
            message = Message(
                content=content,
                sender_id=sender_id,
                timestamp=datetime.now(),
                message_type=message_type,
                metadata=metadata or {}
            )

            strategy = self.strategy_factory.get_strategy(message_type)
            return await strategy.process(message)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "Sorry, there was an error processing your request. Please try again later."

    async def bulk_process_messages(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Process multiple messages in bulk
        """
        responses = []
        for msg in messages:
            response = await self.handle_message(
                content=msg.get('content', ''),
                sender_id=msg.get('sender_id', ''),
                message_type=MessageType(msg.get('message_type', 'OTHER')),
                metadata=msg.get('metadata')
            )
            responses.append(response)
        return responses