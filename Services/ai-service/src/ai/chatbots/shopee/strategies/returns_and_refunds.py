"""
returns_and_refunds.py
Strategy for handling returns and refunds in Shopee.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class RefundStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class RefundRequest:
    user_id: str
    message: str
    created_at: datetime
    ticket_id: str
    status: RefundStatus
    reason: Optional[str] = None
    amount: Optional[float] = None

class RefundValidator:
    @staticmethod
    def validate_request(message: str) -> bool:
        if not message or len(message.strip()) < 10:
            raise ValueError("Message must contain at least 10 characters")
        return True

class TicketingHandler(ABC):
    @abstractmethod
    def create_ticket(self, user_id: str, message: str) -> str:
        pass

    @abstractmethod
    def update_ticket(self, ticket_id: str, status: RefundStatus) -> bool:
        pass

class ReturnsAndRefundsStrategy:
    """
    Handles return and refund processes in Shopee with advanced error handling,
    validation, and status tracking.
    """

    def __init__(self, ticketing_handler: TicketingHandler):
        self.ticketing_handler = ticketing_handler
        self.validator = RefundValidator()
        self._requests: Dict[str, RefundRequest] = {}

    def execute(self, user_id: str, message_text: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the returns and refunds strategy with comprehensive validation and logging.

        Args:
            user_id: The unique identifier of the user
            message_text: The refund request message
            query_info: Additional query information

        Returns:
            Dict containing response and strategy information

        Raises:
            ValueError: If the request is invalid
        """
        try:
            logger.info(f"Processing refund request - user_id: {user_id}")
            
            # Validate request
            self.validator.validate_request(message_text)

            # Create ticket
            ticket_id = self.ticketing_handler.create_ticket(user_id, message_text)

            # Create and store request
            refund_request = RefundRequest(
                user_id=user_id,
                message=message_text,
                created_at=datetime.now(),
                ticket_id=ticket_id,
                status=RefundStatus.PENDING
            )
            self._requests[ticket_id] = refund_request

            response = self._generate_response(ticket_id, refund_request)
            logger.info(f"Refund request processed successfully - ticket_id: {ticket_id}")
            
            return response

        except ValueError as e:
            logger.error(f"Validation error for user {user_id}: {str(e)}")
            return {
                "response": f"Não foi possível processar sua solicitação: {str(e)}",
                "strategy": "returns_and_refunds",
                "status": "error"
            }
        except Exception as e:
            logger.error(f"Unexpected error processing refund for user {user_id}: {str(e)}")
            return {
                "response": "Desculpe, ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.",
                "strategy": "returns_and_refunds",
                "status": "error"
            }

    def _generate_response(self, ticket_id: str, request: RefundRequest) -> Dict[str, Any]:
        """Generates a structured response for the refund request."""
        return {
            "response": (
                f"Sua solicitação de devolução/reembolso foi registrada.\n"
                f"Número do ticket: {ticket_id}\n"
                f"Status: {request.status.value}\n"
                f"Data de abertura: {request.created_at.strftime('%d/%m/%Y %H:%M:%S')}"
            ),
            "strategy": "returns_and_refunds",
            "ticket_id": ticket_id,
            "status": request.status.value,
            "created_at": request.created_at.isoformat()
        }

    def get_request_status(self, ticket_id: str) -> Optional[RefundStatus]:
        """Retrieves the current status of a refund request."""
        request = self._requests.get(ticket_id)
        return request.status if request else None
