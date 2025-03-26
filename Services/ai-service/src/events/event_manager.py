import logging
import datetime
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4
from functools import wraps
import json
from contextlib import contextmanager

from event_producer import send_event
from event_schema import validate_event
from exceptions import EventValidationError, EventPublishError

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class EventResponse:
    """Immutable event response object"""
    event_id: str
    timestamp: str
    type: str
    status: str = "success"
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert response to dictionary"""
        return asdict(self)

class RetryPolicy:
    """Configuration for retry behavior"""
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor

def retry_on_failure(func):
    """Decorator to implement retry logic"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        attempts = 0
        current_delay = self.retry_policy.delay
        last_error = None
        
        while attempts < self.retry_policy.max_retries:
            try:
                return func(self, *args, **kwargs)
            except (EventValidationError, EventPublishError) as e:
                raise e
            except Exception as e:
                last_error = e
                attempts += 1
                if attempts < self.retry_policy.max_retries:
                    logger.warning(f"Retry attempt {attempts} after error: {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= self.retry_policy.backoff_factor
        
        raise EventPublishError(f"Max retries exceeded: {str(last_error)}")
    return wrapper

class EventManager:
    """Advanced event management system with retry policies and monitoring"""
    
    def __init__(self, 
                 topic: str = "ai_predictions",
                 retry_policy: Optional[RetryPolicy] = None,
                 enable_monitoring: bool = True,
                 event_version: str = "1.0",
                 service_name: str = "ai-service"):
        self.topic = topic
        self.retry_policy = retry_policy or RetryPolicy()
        self.enable_monitoring = enable_monitoring
        self.event_version = event_version
        self.service_name = service_name
        self._initialize_metrics()

    def _initialize_metrics(self):
        """Initialize monitoring metrics"""
        self.metrics = {
            "total_events": 0,
            "failed_events": 0,
            "validation_errors": 0,
            "retry_attempts": 0,
            "avg_processing_time": 0.0
        }

    @contextmanager
    def _event_tracking(self):
        """Context manager for event metrics tracking"""
        start_time = datetime.datetime.utcnow()
        try:
            yield
            self.metrics["total_events"] += 1
        except EventValidationError:
            self.metrics["validation_errors"] += 1
            raise
        except Exception:
            self.metrics["failed_events"] += 1
            raise
        finally:
            duration = (datetime.datetime.utcnow() - start_time).total_seconds()
            self._update_avg_processing_time(duration)
            logger.debug(f"Event processing time: {duration}s")

    def _update_avg_processing_time(self, duration: float):
        """Update average processing time metric"""
        total_events = self.metrics["total_events"]
        if total_events > 0:
            current_avg = self.metrics["avg_processing_time"]
            self.metrics["avg_processing_time"] = (current_avg * (total_events - 1) + duration) / total_events

    def _generate_event_id(self) -> str:
        """Generate unique event identifier"""
        return str(uuid4())

    def _create_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create event structure with metadata"""
        return {
            "event_id": self._generate_event_id(),
            "type": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "data": data,
            "version": self.event_version,
            "source": self.service_name,
            "topic": self.topic
        }

    @retry_on_failure
    def publish_event(self, event_type: str, data: Dict[str, Any], **kwargs) -> EventResponse:
        """
        Publish event with validation and retry logic
        
        Args:
            event_type: Type of the event
            data: Event payload
            **kwargs: Additional metadata for the event
            
        Returns:
            EventResponse: Response containing event details
            
        Raises:
            EventValidationError: When event validation fails
            EventPublishError: When event publishing fails
        """
        with self._event_tracking():
            try:
                event = self._create_event(event_type, data)
                event.update(kwargs)  # Add additional metadata
                
                validate_event(event)
                logger.debug(f"Publishing event: {json.dumps(event, indent=2)}")
                
                send_event(self.topic, event)
                logger.info(f"Event published successfully: {event['event_id']}")
                
                return EventResponse(
                    event_id=event["event_id"],
                    timestamp=event["timestamp"],
                    type=event_type,
                    metadata={
                        "topic": self.topic,
                        "version": self.event_version,
                        "source": self.service_name
                    }
                )

            except Exception as e:
                logger.error(f"Error publishing event: {str(e)}", exc_info=True)
                raise EventPublishError(f"Failed to publish event: {str(e)}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
