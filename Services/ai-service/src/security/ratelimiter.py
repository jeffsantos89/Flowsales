# src/security/ratelimiter.py

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import time
from typing import Dict, List, Optional
import threading
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass

class RateLimitStrategy(Enum):
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"

@dataclass
class RateLimitRule:
    limit: int
    interval: int  # in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW

class RateLimiter:
    def __init__(
        self,
        default_rule: RateLimitRule = RateLimitRule(limit=5, interval=60),
        cleanup_interval: int = 300
    ):
        self._storage: Dict[str, List[float]] = defaultdict(list)
        self._rules: Dict[str, RateLimitRule] = {}
        self._default_rule = default_rule
        self._lock = threading.RLock()
        self._last_cleanup = time.time()
        self._cleanup_interval = cleanup_interval

    def add_rule(self, user_id: str, rule: RateLimitRule) -> None:
        """Add a custom rate limit rule for a specific user."""
        with self._lock:
            self._rules[user_id] = rule

    def get_remaining_requests(self, user_id: str) -> int:
        """Get the number of remaining requests allowed for a user."""
