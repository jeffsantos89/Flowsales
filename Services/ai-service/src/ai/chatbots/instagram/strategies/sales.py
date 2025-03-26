from typing import Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import asyncio
from enum import Enum
from uuid import uuid4

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SalesStatus(Enum):
    INITIAL_CONTACT = "initial_contact"
    QUALIFICATION = "qualification"
    NEGOTIATION = "negotiation"
    PROPOSAL = "proposal"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

@dataclass
class Message:
    id: str
    content: str
    timestamp: datetime
    sender: str
    metadata: Dict = None

@dataclass
class Customer:
    instagram_id: str
    username: str
    first_contact: datetime
    last_interaction: datetime
    status: SalesStatus
    engagement_score: float
    conversation_history: List[Message]
    metadata: Dict = None

    def add_message(self, content: str, sender: str) -> None:
        message = Message(
            id=str(uuid4()),
            content=content,
            timestamp=datetime.now(),
            sender=sender,
            metadata={}
        )
        self.conversation_history.append(message)

class EngagementScorer:
    @staticmethod
    def calculate(customer: Customer) -> float:
        """Sophisticated engagement scoring algorithm"""
        days_active = max((datetime.now() - customer.first_contact).days, 1)
        message_count = len(customer.conversation_history)
        response_time_scores = []
        
        # Calculate average response times
        for i in range(1, len(customer.conversation_history)):
            time_diff = (customer.conversation_history[i].timestamp - 
                        customer.conversation_history[i-1].timestamp).total_seconds()
            response_time_scores.append(min(1.0, 3600 / max(time_diff, 1)))

        avg_response_time_score = (
            sum(response_time_scores) / len(response_time_scores)
            if response_time_scores else 0
        )

        # Weighted scoring
        message_frequency_score = min(100, (message_count / days_active) * 10)
        engagement_score = (
            message_frequency_score * 0.6 +
            avg_response_time_score * 40
        )
        
        return min(100, engagement_score)

class SalesStrategy(ABC):
    @abstractmethod
    async def execute(self, customer: Customer, message: str) -> str:
        pass

    @abstractmethod
    def can_handle(self, customer: Customer, message: str) -> bool:
        pass

class InitialContactStrategy(SalesStrategy):
    async def execute(self, customer: Customer, message: str) -> str:
        customer.status = SalesStatus.QUALIFICATION
        return "Welcome! How can I assist you today?"

    def can_handle(self, customer: Customer, message: str) -> bool:
        return customer.status == SalesStatus.INITIAL_CONTACT

class QualificationStrategy(SalesStrategy):
    QUALIFYING_KEYWORDS = ['interested', 'looking for', 'need', 'want']

    async def execute(self, customer: Customer, message: str) -> str:
        if self._is_qualified(message):
            customer.status = SalesStatus.NEGOTIATION
            return "Excellent! Let me show you our offerings..."
        return "Could you tell me more about what you're looking for?"

    def can_handle(self, customer: Customer, message: str) -> bool:
        return customer.status == SalesStatus.QUALIFICATION

    def _is_qualified(self, message: str) -> bool:
        return any(keyword in message.lower() for keyword in self.QUALIFYING_KEYWORDS)

# Similar implementation for other strategies...

class InstagramSalesManager:
    def __init__(self):
        self.strategies: List[SalesStrategy] = [
            InitialContactStrategy(),
            QualificationStrategy(),
            # Add other strategies...
        ]
        self.customers: Dict[str, Customer] = {}
        self.engagement_scorer = EngagementScorer()

    async def handle_message(self, instagram_id: str, username: str, message: str) -> str:
        try:
            customer = await self._get_or_create_customer(instagram_id, username)
            customer.add_message(message, sender="customer")

            strategy = self._get_appropriate_strategy(customer, message)
            if not strategy:
                logger.warning(f"No strategy found for status {customer.status}")
                return "I'll connect you with a human representative."

            response = await strategy.execute(customer, message)
            customer.add_message(response, sender="bot")
            
            await self._update_customer_interaction(customer)
            return response

        except Exception as e:
            logger.exception("Error processing message")
            return "I apologize, but I'm experiencing technical difficulties."

    def _get_appropriate_strategy(self, customer: Customer, message: str) -> Optional[SalesStrategy]:
        return next(
            (strategy for strategy in self.strategies 
             if strategy.can_handle(customer, message)),
            None
        )

    async def _get_or_create_customer(self, instagram_id: str, username: str) -> Customer:
        if instagram_id not in self.customers:
            self.customers[instagram_id] = Customer(
                instagram_id=instagram_id,
                username=username,
                first_contact=datetime.now(),
                last_interaction=datetime.now(),
                status=SalesStatus.INITIAL_CONTACT,
                engagement_score=0.0,
                conversation_history=[],
                metadata={}
            )
        return self.customers[instagram_id]

    async def _update_customer_interaction(self, customer: Customer):
        customer.last_interaction = datetime.now()
        customer.engagement_score = self.engagement_scorer.calculate(customer)
