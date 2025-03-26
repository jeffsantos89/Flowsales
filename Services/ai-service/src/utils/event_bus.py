import threading
from collections import defaultdict
from typing import Callable, Dict, List, Any

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, listener: Callable[[Any], None]) -> None:
        with self._lock:
            self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: Callable[[Any], None]) -> None:
        with self._lock:
            if event_type in self._listeners:
                self._listeners[event_type].remove(listener)
                if not self._listeners[event_type]:
                    del self._listeners[event_type]

    def publish(self, event_type: str, event: Any) -> None:
        with self._lock:
            listeners = list(self._listeners.get(event_type, []))
        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                # Log the exception or handle it as needed
                print(f"Error handling event {event_type}: {e}")

    def clear(self) -> None:
        with self._lock:
            self._listeners.clear()

# Example usage:
# def handle_event(event):
#     print(f"Handled event: {event}")

# bus = EventBus()
# bus.subscribe("test_event", handle_event)
# bus.publish("test_event", {"key": "value"})
# bus.unsubscribe("test_event", handle_event)
# bus.clear()