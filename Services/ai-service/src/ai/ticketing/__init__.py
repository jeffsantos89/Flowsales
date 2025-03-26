# src/ai/ticketing/__init__.py

from dataclasses import dataclass
from datetime import datetime
import uuid
from enum import Enum
from typing import Optional, Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Ticket:
    id: str
    user_id: str
    message: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None
    tags: List[str] = None
    metadata: Dict = None

class TicketingSystem:
    def __init__(self):
        self._tickets: Dict[str, Ticket] = {}

    def create_ticket(
        self,
        user_id: str,
        message: str,
        priority: TicketPriority = TicketPriority.MEDIUM,
        tags: List[str] = None,
        metadata: Dict = None
    ) -> str:
        """
        Create a new ticket in the system.
        
        Args:
            user_id: The ID of the user creating the ticket
            message: The ticket message/description
            priority: Ticket priority level
            tags: List of tags associated with the ticket
            metadata: Additional metadata for the ticket
            
        Returns:
            str: The created ticket ID
        """
        try:
            ticket_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            ticket = Ticket(
                id=ticket_id,
                user_id=user_id,
                message=message,
                status=TicketStatus.OPEN,
                priority=priority,
                created_at=current_time,
                updated_at=current_time,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            self._tickets[ticket_id] = ticket
            
            logger.info(
                f"Ticket created: {ticket_id} | User: {user_id} | Priority: {priority.value}"
            )
            
            return ticket_id
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            raise

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Retrieve a ticket by its ID."""
        return self._tickets.get(ticket_id)

    def update_ticket_status(self, ticket_id: str, status: TicketStatus) -> bool:
        """Update the status of an existing ticket."""
        if ticket_id in self._tickets:
            ticket = self._tickets[ticket_id]
            ticket.status = status
            ticket.updated_at = datetime.utcnow()
            logger.info(f"Ticket {ticket_id} status updated to {status.value}")
            return True
        return False

    def assign_ticket(self, ticket_id: str, agent_id: str) -> bool:
        """Assign a ticket to a support agent."""
        if ticket_id in self._tickets:
            ticket = self._tickets[ticket_id]
            ticket.assigned_to = agent_id
            ticket.updated_at = datetime.utcnow()
            logger.info(f"Ticket {ticket_id} assigned to agent {agent_id}")
            return True
        return False
