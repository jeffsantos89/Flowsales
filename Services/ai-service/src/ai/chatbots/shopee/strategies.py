from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
import logging
from datetime import datetime
import asyncio
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotIntent(Enum):
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    PRICE_CHECK = "price_check"
    ORDER_STATUS = "order_status"
    CUSTOMER_SUPPORT = "customer_support"
    UNKNOWN = "unknown"

@dataclass
class ChatContext:
    user_id: str
    session_id: str
    timestamp: datetime
    message: str
    intent: ChatbotIntent
    metadata: Dict[str, Any]

class ResponseStrategy(ABC):
    """Abstract base class for chatbot response strategies"""
    
    @abstractmethod
    async def process(self, context: ChatContext) -> Dict[str, Any]:
        """Process the input context and return appropriate response"""
        pass

    def _validate_context(self, context: ChatContext) -> bool:
        """Validate the chat context"""
        return all([
            context.user_id,
            context.session_id,
            context.message,
            isinstance(context.timestamp, datetime)
        ])

class GreetingStrategy(ResponseStrategy):
    async def process(self, context: ChatContext) -> Dict[str, Any]:
        if not self._validate_context(context):
            raise ValueError("Invalid context provided")
        
        try:
            return {
                "type": "greeting",
                "message": f"Hello! Welcome to Shopee. How can I assist you today?",
                "suggestions": ["View Products", "Track Order", "Customer Support"]
            }
        except Exception as e:
            logger.error(f"Error in GreetingStrategy: {str(e)}")
            raise

class ProductInquiryStrategy(ResponseStrategy):
    async def process(self, context: ChatContext) -> Dict[str, Any]:
        if not self._validate_context(context):
            raise ValueError("Invalid context provided")
        
        try:
            # Here you would typically integrate with your product database
            return {
                "type": "product_inquiry",
                "message": "I'll help you find the product you're looking for.",
                "action": "search_products",
                "parameters": {"query": context.message}
            }
        except Exception as e:
            logger.error(f"Error in ProductInquiryStrategy: {str(e)}")
            raise

class StrategyFactory:
    """Factory class for creating response strategies"""
    
    _strategies: Dict[ChatbotIntent, ResponseStrategy] = {
        ChatbotIntent.GREETING: GreetingStrategy(),
        ChatbotIntent.PRODUCT_INQUIRY: ProductInquiryStrategy(),
        # Add more strategies as needed
    }

    @classmethod
    def get_strategy(cls, intent: ChatbotIntent) -> ResponseStrategy:
        """Get the appropriate strategy based on intent"""
        try:
            return cls._strategies[intent]
        except KeyError:
            logger.warning(f"No strategy found for intent: {intent}")
            return cls._strategies.get(ChatbotIntent.UNKNOWN, GreetingStrategy())

class ShopeeBot:
    """Main chatbot orchestrator"""
    
    def __init__(self):
        self.strategy_factory = StrategyFactory()
        self.active_sessions: Dict[str, ChatContext] = {}

    async def process_message(self, user_id: str, message: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Process incoming messages and return appropriate responses"""
        try:
            # Create context
            context = ChatContext(
                user_id=user_id,
                session_id=f"session_{user_id}_{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                message=message,
                intent=self._detect_intent(message),
                metadata=metadata or {}
            )

            # Get and execute appropriate strategy
            strategy = self.strategy_factory.get_strategy(context.intent)
            response = await strategy.process(context)

            # Update session
            self.active_sessions[context.session_id] = context

            return response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "type": "error",
                "message": "I apologize, but I'm having trouble processing your request. Please try again later."
            }

    def _detect_intent(self, message: str) -> ChatbotIntent:
        """Detect intent from user message"""
        # This is a simplified version. In production, you'd want to use
        # more sophisticated NLP/ML models for intent classification
        message = message.lower()
        
        if any(word in message for word in ["hello", "hi", "hey"]):
            return ChatbotIntent.GREETING
        elif any(word in message for word in ["product", "item", "buy"]):
            return ChatbotIntent.PRODUCT_INQUIRY
        else:
            return ChatbotIntent.UNKNOWN

    async def cleanup_sessions(self, max_age_hours: int = 24):
        """Cleanup old sessions"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = [
                    session_id for session_id, context in self.active_sessions.items()
                    if (current_time - context.timestamp).total_seconds() > max_age_hours * 3600
                ]
                
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
                
                await asyncio.sleep(3600)  # Clean up every hour
            except Exception as e:
                logger.error(f"Error in cleanup_sessions: {str(e)}")
                await asyncio.sleep(3600)