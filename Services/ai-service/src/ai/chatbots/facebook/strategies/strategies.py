from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MessageContext:
    """Data class to hold message context information"""
    sender_id: str
    message_text: Optional[str]
    timestamp: datetime
    payload: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class FacebookStrategy(ABC):
    """Abstract base class for Facebook message handling strategies"""
    
    @abstractmethod
    async def handle_message(self, context: MessageContext) -> Dict[str, Any]:
        """Abstract method to handle incoming messages"""
        pass

    def validate_context(self, context: MessageContext) -> bool:
        """Validate the message context"""
        return bool(context and context.sender_id)

class TextMessageStrategy(FacebookStrategy):
    """Strategy for handling text messages"""
    
    async def handle_message(self, context: MessageContext) -> Dict[str, Any]:
        try:
            if not self.validate_context(context):
                raise ValueError("Invalid message context")
            
            logger.info(f"Processing text message from {context.sender_id}")
            
            # Process text message logic here
            response = {
                "recipient": {"id": context.sender_id},
                "message": {"text": f"Received your message: {context.message_text}"}
            }
            
            return response
        except Exception as e:
            logger.error(f"Error processing text message: {str(e)}")
            raise

class QuickReplyStrategy(FacebookStrategy):
    """Strategy for handling quick replies"""
    
    async def handle_message(self, context: MessageContext) -> Dict[str, Any]:
        try:
            if not self.validate_context(context):
                raise ValueError("Invalid message context")
            
            logger.info(f"Processing quick reply from {context.sender_id}")
            
            # Process quick reply logic here
            response = {
                "recipient": {"id": context.sender_id},
                "message": {
                    "text": "Choose an option:",
                    "quick_replies": [
                        {
                            "content_type": "text",
                            "title": "Option 1",
                            "payload": "OPTION_1"
                        },
                        {
                            "content_type": "text",
                            "title": "Option 2",
                            "payload": "OPTION_2"
                        }
                    ]
                }
            }
            
            return response
        except Exception as e:
            logger.error(f"Error processing quick reply: {str(e)}")
            raise

class PostbackStrategy(FacebookStrategy):
    """Strategy for handling postback actions"""
    
    async def handle_message(self, context: MessageContext) -> Dict[str, Any]:
        try:
            if not self.validate_context(context):
                raise ValueError("Invalid message context")
            
            logger.info(f"Processing postback from {context.sender_id}")
            
            # Process postback logic here
            response = {
                "recipient": {"id": context.sender_id},
                "message": {"text": "Processed your selection"}
            }
            
            return response
        except Exception as e:
            logger.error(f"Error processing postback: {str(e)}")
            raise

class StrategyFactory:
    """Factory class for creating message handling strategies"""
    
    @staticmethod
    def create_strategy(message_type: str) -> FacebookStrategy:
        strategies = {
            "text": TextMessageStrategy(),
            "quick_reply": QuickReplyStrategy(),
            "postback": PostbackStrategy()
        }
        
        strategy = strategies.get(message_type.lower())
        if not strategy:
            raise ValueError(f"Unknown message type: {message_type}")
        
        return strategy

class FacebookMessageHandler:
    """Main handler class for Facebook messages"""
    
    def __init__(self):
        self.strategy_factory = StrategyFactory()
    
    async def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Extract message type and create context
            message_type = self._determine_message_type(event)
            context = self._create_message_context(event)
            
            # Get appropriate strategy and handle message
            strategy = self.strategy_factory.create_strategy(message_type)
            response = await strategy.handle_message(context)
            
            return response
        except Exception as e:
            logger.error(f"Error handling webhook event: {str(e)}")
            raise
    
    def _determine_message_type(self, event: Dict[str, Any]) -> str:
        """Determine the type of message from the event"""
        if "message" in event:
            if "quick_reply" in event["message"]:
                return "quick_reply"
            return "text"
        elif "postback" in event:
            return "postback"
        else:
            raise ValueError("Unknown event type")
    
    def _create_message_context(self, event: Dict[str, Any]) -> MessageContext:
        """Create MessageContext from event data"""
        return MessageContext(
            sender_id=event.get("sender", {}).get("id"),
            message_text=event.get("message", {}).get("text"),
            timestamp=datetime.fromtimestamp(event.get("timestamp", 0) / 1000),
            payload=event.get("postback", {}).get("payload"),
            metadata=event
        )