# src/ai/queue/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import uuid
import logging
from dataclasses import dataclass

@dataclass
class Message:
    """Data class representing a queue message"""
    id: str
    topic: str
    payload: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    status: str = "pending"

class QueueException(Exception):
    """Base exception for queue operations"""
    pass

class MessageQueue(ABC):
    """Abstract base class for message queue implementations"""
    
    def __init__(self, max_retries: int = 3):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_retries = max_retries

    @abstractmethod
    async def enqueue(self, topic: str, payload: Dict[str, Any]) -> str:
        """
        Enqueue a message to the specified topic
        
        Args:
            topic: The topic/queue name
            payload: Message payload as dictionary
            
        Returns:
            str: Message ID
            
        Raises:
            QueueException: If enqueue operation fails
        """
        pass

    @abstractmethod
    async def dequeue(self, topic: str) -> Optional[Message]:
        """Retrieve and remove a message from the queue"""
        pass

    @abstractmethod
    async def peek(self, topic: str) -> Optional[Message]:
        """View next message without removing it"""
        pass

    @abstractmethod
    async def ack(self, message_id: str) -> bool:
        """Acknowledge message processing"""
        pass

    @abstractmethod
    async def nack(self, message_id: str) -> bool:
        """Report failed message processing"""
        pass

    def create_message(self, topic: str, payload: Dict[str, Any]) -> Message:
        """Create a new message instance"""
        return Message(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            timestamp=datetime.utcnow()
        )

    async def __aenter__(self):
        """Context manager support"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources on exit"""
        await self.cleanup()

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup queue resources"""
        pass
