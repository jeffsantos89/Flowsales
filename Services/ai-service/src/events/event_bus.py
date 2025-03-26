import asyncio
from typing import Any, Callable, Dict, List, Optional
import logging
from functools import partial

class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, callback):
        """Adiciona um listener a um evento"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    async def publish(self, event_type, data):
        """Dispara eventos para todos os listeners"""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                await callback(data)

event_bus = EventBus()
class EventBusError(Exception):
    """Base exception for EventBus errors"""
    pass

class EventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        
    async def subscribe(self, event_type: str, callback: Callable, max_retries: int = 3) -> None:
        """Subscribe a callback to an event type with retry mechanism"""
        async with self._lock:
            try:
                if not callable(callback):
                    raise EventBusError(f"Callback must be callable, got {type(callback)}")
                
                if event_type not in self.listeners:
                    self.listeners[event_type] = []
                
                if callback not in self.listeners[event_type]:
                    self.listeners[event_type].append(callback)
                    self.logger.info(f"Subscribed {callback.__name__} to {event_type}")
            except Exception as e:
                self.logger.error(f"Error subscribing to {event_type}: {str(e)}")
                raise EventBusError(f"Subscription failed: {str(e)}")

    async def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Remove a callback from an event type"""
        async with self._lock:
            try:
                if event_type in self.listeners:
                    self.listeners[event_type].remove(callback)
                    self.logger.info(f"Unsubscribed {callback.__name__} from {event_type}")
            except ValueError:
                self.logger.warning(f"Callback {callback.__name__} not found for {event_type}")

    async def publish(self, event_type: str, data: Any, timeout: float = 5.0) -> None:
        """Publish an event with timeout and concurrent execution"""
        if event_type not in self.listeners:
            self.logger.debug(f"No listeners for event {event_type}")
            return

        tasks = []
        for callback in self.listeners[event_type]:
            task = asyncio.create_task(self._execute_callback(callback, data))
            tasks.append(task)

        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.error(f"Event {event_type} processing timed out after {timeout}s")
            for task in tasks:
                task.cancel()
        except Exception as e:
            self.logger.error(f"Error publishing event {event_type}: {str(e)}")
            raise EventBusError(f"Publishing failed: {str(e)}")

    async def _execute_callback(self, callback: Callable, data: Any) -> None:
        """Execute a callback with error handling"""
        try:
            await callback(data)
        except Exception as e:
            self.logger.error(f"Error in callback {callback.__name__}: {str(e)}")

    def clear_all(self) -> None:
        """Clear all event listeners"""
        self.listeners.clear()
        self.logger.info("All event listeners cleared")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Singleton instance
event_bus = EventBus()