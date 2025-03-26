from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from pydantic import BaseModel, Field
from contextlib import contextmanager
import asyncio
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TicketStatus(str, Enum):
    """Enum for ticket statuses with valid transitions"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

    @classmethod
    def valid_transitions(cls) -> Dict[str, List[str]]:
        return {
            cls.OPEN: [cls.IN_PROGRESS, cls.CLOSED],
            cls.IN_PROGRESS: [cls.RESOLVED, cls.CLOSED],
            cls.RESOLVED: [cls.CLOSED, cls.IN_PROGRESS],
            cls.CLOSED: [cls.OPEN]
        }

@dataclass
class TicketPriority(str, Enum):
    """Enum for ticket priorities with SLA times"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def sla_hours(self) -> int:
        """Returns SLA time in hours for each priority level"""
        return {
            self.LOW: 48,
            self.MEDIUM: 24,
            self.HIGH: 4,
            self.CRITICAL: 1
        }[self]

class TicketValidationError(Exception):
    """Custom exception for ticket validation errors"""
    pass

class TicketModel(BaseModel):
    """Pydantic model for ticket validation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    assignee: Optional[str] = None
    resolution: Optional[str] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        use_enum_values = True

def audit_log(func):
    """Decorator for auditing ticket operations"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = datetime.now(timezone.utc)
        result = await func(self, *args, **kwargs)
        
        if hasattr(self, 'history'):
            self.history.append({
                'operation': func.__name__,
                'timestamp': start_time,
                'args': args,
                'kwargs': {k: v for k, v in kwargs.items() if k != 'self'}
            })
        
        return result
    return wrapper

class TicketBase:
    """Enhanced base class for ticket implementation"""
    def __init__(
        self, 
        user_id: str, 
        message: str,
        priority: TicketPriority = TicketPriority.MEDIUM
    ):
        self._ticket = TicketModel(
            user_id=user_id,
            message=message,
            priority=priority
        )

    @property
    def id(self) -> str:
        return self._ticket.id

    def _validate_status_transition(self, new_status: TicketStatus) -> bool:
        """Validate if status transition is allowed"""
        valid_transitions = TicketStatus.valid_transitions().get(self._ticket.status, [])
        return new_status in valid_transitions

    @audit_log
    async def update_status(self, new_status: TicketStatus) -> None:
        """Update ticket status with validation"""
        if not self._validate_status_transition(new_status):
            raise TicketValidationError(
                f"Invalid status transition from {self._ticket.status} to {new_status}"
            )
        self._ticket.status = new_status
        self._ticket.updated_at = datetime.now(timezone.utc)

    @audit_log
    async def assign_to(self, assignee_id: str) -> None:
        """Assign ticket to a support agent"""
        self._ticket.assignee = assignee_id
        self._ticket.updated_at = datetime.now(timezone.utc)

    @audit_log
    async def add_resolution(self, resolution: str) -> None:
        """Add resolution details to ticket"""
        self._ticket.resolution = resolution
        self._ticket.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert ticket to dictionary"""
        return self._ticket.dict()

class TicketRepository(ABC):
    """Abstract base class for ticket storage with retry mechanism"""
    @abstractmethod
    async def save(self, ticket: TicketBase) -> None:
        pass

    @abstractmethod
    async def get(self, ticket_id: str) -> Optional[TicketBase]:
        pass

    @abstractmethod
    async def list_by_status(self, status: TicketStatus) -> List[TicketBase]:
        pass

    @abstractmethod
    async def list_by_priority(self, priority: TicketPriority) -> List[TicketBase]:
        pass

    @contextmanager
    async def retry_operation(self, max_retries: int = 3, delay: float = 1.0):
        """Context manager for retrying operations"""
        retries = 0
        while True:
            try:
                yield
                break
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise
                logger.warning(f"Retry {retries}/{max_retries} after error: {str(e)}")
                await asyncio.sleep(delay * retries)

class TicketingSystem:
    """Enhanced ticket management system"""
    def __init__(self, repository: TicketRepository):
        self.repository = repository

    @audit_log
    async def create_ticket(
        self, 
        user_id: str, 
        message: str,
        priority: TicketPriority = TicketPriority.MEDIUM
    ) -> TicketBase:
        """Creates a new support ticket with retry mechanism"""
        async with self.repository.retry_operation():
            ticket = TicketBase(user_id, message, priority)
            await self.repository.save(ticket)
            logger.info(f"Created ticket {ticket.id} for user {user_id}")
            return ticket

    async def get_ticket(self, ticket_id: str) -> Optional[TicketBase]:
        """Retrieves a specific ticket"""
        async with self.repository.retry_operation():
            return await self.repository.get(ticket_id)

    async def list_tickets_by_status(self, status: TicketStatus) -> List[TicketBase]:
        """Returns all tickets with specified status"""
        async with self.repository.retry_operation():
            return await self.repository.list_by_status(status)

    async def list_tickets_by_priority(self, priority: TicketPriority) -> List[TicketBase]:
        """Returns all tickets with specified priority"""
        async with self.repository.retry_operation():
            return await self.repository.list_by_priority(priority)

    @audit_log
    async def update_ticket_status(
        self, 
        ticket_id: str, 
        new_status: TicketStatus
    ) -> Optional[TicketBase]:
        """Updates ticket status with validation"""
        async with self.repository.retry_operation():
            ticket = await self.get_ticket(ticket_id)
            if ticket:
                await ticket.update_status(new_status)
                await self.repository.save(ticket)
                logger.info(f"Updated ticket {ticket_id} status to {new_status}")
            return ticket
