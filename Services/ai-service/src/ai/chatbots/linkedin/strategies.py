from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio
from dataclasses import dataclass
from enum import Enum
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkedInMessageType(Enum):
    CONNECT_REQUEST = "connect_request"
    FOLLOW_UP = "follow_up"
    ENGAGEMENT = "engagement"
    SALES_OUTREACH = "sales_outreach"
    NETWORKING = "networking"

@dataclass
class MessageContext:
    prospect_name: str
    prospect_title: Optional[str]
    company: Optional[str]
    mutual_connections: int
    last_interaction: Optional[datetime]
    custom_variables: Dict[str, Any]

class LinkedInStrategy(ABC):
    """Abstract base class for LinkedIn messaging strategies"""
    
    @abstractmethod
    async def execute(self, context: MessageContext) -> Dict[str, Any]:
        """Execute the strategy and return the result"""
        pass

    def validate_context(self, context: MessageContext) -> bool:
        """Validate if the context has required information"""
        return bool(context and context.prospect_name)

class ConnectionRequestStrategy(LinkedInStrategy):
    async def execute(self, context: MessageContext) -> Dict[str, Any]:
        try:
            if not self.validate_context(context):
                raise ValueError("Invalid context for connection request")

            message = self._generate_connection_message(context)
            
            return {
                "type": LinkedInMessageType.CONNECT_REQUEST.value,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context
            }
        except Exception as e:
            logger.error(f"Error in ConnectionRequestStrategy: {str(e)}")
            raise

    def _generate_connection_message(self, context: MessageContext) -> str:
        return f"Hi {context.prospect_name}, I noticed your work at {context.company or 'your company'} and would love to connect!"

class FollowUpStrategy(LinkedInStrategy):
    async def execute(self, context: MessageContext) -> Dict[str, Any]:
        try:
            if not self.validate_context(context):
                raise ValueError("Invalid context for follow-up")

            message = self._generate_follow_up_message(context)
            
            return {
                "type": LinkedInMessageType.FOLLOW_UP.value,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context
            }
        except Exception as e:
            logger.error(f"Error in FollowUpStrategy: {str(e)}")
            raise

    def _generate_follow_up_message(self, context: MessageContext) -> str:
        return f"Hi {context.prospect_name}, thank you for connecting! I'd love to learn more about your work at {context.company or 'your company'}."

class LinkedInStrategyFactory:
    """Factory class for creating LinkedIn strategies"""
    
    _strategies: Dict[LinkedInMessageType, LinkedInStrategy] = {
        LinkedInMessageType.CONNECT_REQUEST: ConnectionRequestStrategy(),
        LinkedInMessageType.FOLLOW_UP: FollowUpStrategy(),
    }

    @classmethod
    def get_strategy(cls, strategy_type: LinkedInMessageType) -> LinkedInStrategy:
        strategy = cls._strategies.get(strategy_type)
        if not strategy:
            raise ValueError(f"Strategy not found for type: {strategy_type}")
        return strategy

    @classmethod
    def register_strategy(cls, type_: LinkedInMessageType, strategy: LinkedInStrategy):
        cls._strategies[type_] = strategy

class LinkedInMessageOrchestrator:
    """Orchestrator for handling LinkedIn messaging strategies"""

    def __init__(self):
        self.factory = LinkedInStrategyFactory()

    async def process_message(
        self,
        strategy_type: LinkedInMessageType,
        context: MessageContext
    ) -> Dict[str, Any]:
        try:
            strategy = self.factory.get_strategy(strategy_type)
            result = await strategy.execute(context)
            
            # Log the successful execution
            logger.info(
                f"Successfully executed {strategy_type.value} strategy for {context.prospect_name}"
            )
            
            return result
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    async def batch_process_messages(
        self,
        contexts: List[MessageContext],
        strategy_type: LinkedInMessageType
    ) -> List[Dict[str, Any]]:
        tasks = [
            self.process_message(strategy_type, context)
            for context in contexts
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Example usage
"""
orchestrator = LinkedInMessageOrchestrator()

context = MessageContext(
    prospect_name="John Doe",
    prospect_title="Software Engineer",
    company="Tech Corp",
    mutual_connections=5,
    last_interaction=None,
    custom_variables={"industry": "Technology"}
)

result = await orchestrator.process_message(
    LinkedInMessageType.CONNECT_REQUEST,
    context
)
"""