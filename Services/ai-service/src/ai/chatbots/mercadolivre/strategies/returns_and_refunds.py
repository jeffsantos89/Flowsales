"""
returns_and_refunds.py
Strategy for handling product returns and refunds in a robust and scalable way.
"""

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Dict, Any, Optional
from enum import Enum
from ai.ticketing import TicketingSystem
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RefundStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"

@dataclass
class RefundRequest:
    user_id: str
    query_text: str
    timestamp: datetime
    order_id: Optional[str] = None
    reason: Optional[str] = None
    amount: Optional[float] = None

class RefundValidator:
    @staticmethod
    def validate_request(query_info: Dict[str, Any]) -> bool:
        required_fields = ['user_id', 'query_text']
        return all(field in query_info for field in required_fields)

class ReturnsAndRefundsStrategy:
    def __init__(self, ticketing: TicketingSystem):
        self.ticketing = ticketing
        self.validator = RefundValidator()

    def _extract_order_info(self, query_text: str) -> Optional[str]:
        """Extract order ID from query text using basic pattern matching."""
        # Implementation would depend on your specific needs
        return None

    def _categorize_refund_reason(self, query_text: str) -> str:
        """Categorize the refund reason based on query text."""
        # Add your categorization logic here
        return "general_refund"

    def _create_refund_request(self, user_id: str, query_text: str) -> RefundRequest:
        return RefundRequest(
            user_id=user_id,
            query_text=query_text,
            timestamp=datetime.utcnow(),
            order_id=self._extract_order_info(query_text),
            reason=self._categorize_refund_reason(query_text)
        )

    def execute(self, user_id: str, query_text: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the returns and refunds strategy.
        
        Args:
            user_id: Unique identifier for the user
            query_text: The user's refund request text
            query_info: Additional information about the request
            
        Returns:
            Dict containing response and strategy information
            
        Raises:
            ValueError: If the request validation fails
        """
        try:
            logger.info(f"[ReturnsAndRefundsStrategy] Processing request for user_id={user_id}")
            
            if not self.validator.validate_request(query_info):
                raise ValueError("Invalid request parameters")

            # Create structured refund request
            refund_request = self._create_refund_request(user_id, query_text)
            
            # Create ticket with structured information
            ticket_metadata = {
                "refund_request": refund_request.__dict__,
                "status": RefundStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat()
            }
            
            ticket_id = self.ticketing.create_ticket(
                user_id=user_id,
                description=query_text,
                metadata=ticket_metadata
            )

            logger.info(f"[ReturnsAndRefundsStrategy] Created ticket {ticket_id} for user {user_id}")

            return {
                "response": (
                    f"Sua solicitação de devolução/reembolso foi registrada com sucesso.\n"
                    f"Número do ticket: {ticket_id}\n"
                    f"Status: {RefundStatus.PENDING.value}"
                ),
                "strategy": "returns",
                "ticket_id": ticket_id,
                "status": RefundStatus.PENDING.value,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"[ReturnsAndRefundsStrategy] Error processing refund request: {str(e)}")
            raise
