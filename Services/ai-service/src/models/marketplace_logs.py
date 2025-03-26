from typing import Optional, Dict, Any
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

@dataclass
class MarketplaceLog:
    """
    A class to handle marketplace logging with enhanced features and type safety.
    """
    timestamp: datetime
    level: LogLevel
    marketplace: str
    action: str
    details: Dict[str, Any]
    status: str
    trace_id: str
    
    def __init__(
        self,
        marketplace: str,
        action: str,
        details: Dict[str, Any],
        level: LogLevel = LogLevel.INFO,
        status: str = "SUCCESS",
        trace_id: Optional[str] = None
    ):
        self.timestamp = datetime.utcnow()
        self.level = level
        self.marketplace = marketplace
        self.action = action
        self.details = details
        self.status = status
        self.trace_id = trace_id or self._generate_trace_id()

    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID."""
        from uuid import uuid4
        return str(uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary format."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "marketplace": self.marketplace,
            "action": self.action,
            "details": self.details,
            "status": self.status,
            "trace_id": self.trace_id
        }

    def log(self) -> None:
        """Log the entry using Python's logging module."""
        log_message = f"[{self.marketplace}] {self.action} - Status: {self.status} (Trace: {self.trace_id})"
        
        if self.level == LogLevel.ERROR:
            logger.error(log_message, extra=self.to_dict())
        elif self.level == LogLevel.WARNING:
            logger.warning(log_message, extra=self.to_dict())
        elif self.level == LogLevel.DEBUG:
            logger.debug(log_message, extra=self.to_dict())
        else:
            logger.info(log_message, extra=self.to_dict())

    @classmethod
    def error(cls, marketplace: str, action: str, details: Dict[str, Any], **kwargs) -> 'MarketplaceLog':
        """Create an error log entry."""
        return cls(marketplace, action, details, level=LogLevel.ERROR, status="ERROR", **kwargs)

    @classmethod
    def warning(cls, marketplace: str, action: str, details: Dict[str, Any], **kwargs) -> 'MarketplaceLog':
        """Create a warning log entry."""
        return cls(marketplace, action, details, level=LogLevel.WARNING, **kwargs)