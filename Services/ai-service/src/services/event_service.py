from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from functools import wraps
import asyncio
from dataclasses import dataclass
import json
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Event data structure."""
    id: str
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    status: str
    source: str
    version: str = "1.0"

class EventServiceError(Exception):
    """Custom exception for EventService errors."""
    pass

def error_handler(func):
    """Decorator for handling errors in service methods."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise EventServiceError(f"Service error: {str(e)}")
    return wrapper

class EventService:
    """
    Event handling service with advanced features for production use.
    Implements async operations, retry mechanisms, and proper error handling.
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self._events: List[Event] = []
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._handlers: Dict[str, List[callable]] = {}

    @error_handler
    async def create_event(self, event_type: str, data: Dict[str, Any], source: str) -> Event:
        """
        Create and store a new event.
        """
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            status="CREATED",
            source=source
        )
        
        self._events.append(event)
        logger.info(f"Created event: {event.id} of type {event.type}")
        await self._process_event(event)
        return event

    @error_handler
    async def get_event(self, event_id: str) -> Optional[Event]:
        """
        Retrieve an event by its ID.
        """
        return next((event for event in self._events if event.id == event_id), None)

    @error_handler
    async def list_events(self, 
                         event_type: Optional[str] = None, 
                         source: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Event]:
        """
        List events with optional filtering.
        """
        filtered_events = self._events

        if event_type:
            filtered_events = [e for e in filtered_events if e.type == event_type]
        if source:
            filtered_events = [e for e in filtered_events if e.source == source]
        if start_date:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
        if end_date:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_date]

        return filtered_events

    async def register_handler(self, event_type: str, handler: callable) -> None:
        """
        Register an event handler for a specific event type.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")

    async def _process_event(self, event: Event) -> None:
        """
        Process an event with registered handlers using retry mechanism.
        """
        if event.type not in self._handlers:
            return

        for handler in self._handlers[event.type]:
            for attempt in range(self._max_retries):
                try:
                    event.status = "PROCESSING"
                    await handler(event)
                    event.status = "COMPLETED"
                    logger.info(f"Successfully processed event {event.id}")
                    break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for event {event.id}: {str(e)}")
                    if attempt == self._max_retries - 1:
                        event.status = "FAILED"
                        logger.error(f"Failed to process event {event.id} after {self._max_retries} attempts")
                        raise
                    await asyncio.sleep(self._retry_delay * (attempt + 1))

    def serialize_event(self, event: Event) -> str:
        """
        Serialize event to JSON string.
        """
        return json.dumps({
            'id': event.id,
            'type': event.type,
            'data': event.data,
            'timestamp': event.timestamp.isoformat(),
            'status': event.status,
            'source': event.source,
            'version': event.version
        })

    @classmethod
    def deserialize_event(cls, event_json: str) -> Event:
        """
        Deserialize JSON string to Event object.
        """
        data = json.loads(event_json)
        return Event(
            id=data['id'],
            type=data['type'],
            data=data['data'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            status=data['status'],
            source=data['source'],
            version=data.get('version', '1.0')
        )

    async def cleanup_old_events(self, days_to_keep: int = 30) -> None:
        """
        Clean up events older than specified days.
        """
        threshold = datetime.utcnow() - timedelta(days=days_to_keep)
        self._events = [e for e in self._events if e.timestamp >= threshold]
        logger.info(f"Cleaned up events older than {days_to_keep} days")