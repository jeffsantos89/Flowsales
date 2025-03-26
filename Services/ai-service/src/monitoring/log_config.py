import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import traceback
from logging.handlers import RotatingFileHandler
import os

class EnhancedJSONFormatter(logging.Formatter):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line_number": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
            "logger_name": record.name
        }

        if hasattr(record, 'props'):
            log_record.update(record.props)

        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'stacktrace': traceback.format_exception(*record.exc_info)
            }

        return json.dumps(log_record, default=str)

def configure_logger(
    name: str = "app",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure a logger with both console and file handlers.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(EnhancedJSONFormatter())
    logger.addHandler(console_handler)

    # File handler (if log_file is specified)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(EnhancedJSONFormatter())
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger

# Example usage
logger = configure_logger(
    name="flowsale",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file="logs/application.log"
)

# Add a custom logging method for structured logging
def structured_log(logger: logging.Logger, level: str, message: str, **props):
    """
    Create a structured log entry with additional properties.
    """
    log_func = getattr(logger, level.lower())
    record = logging.LogRecord(
        name=logger.name,
        level=getattr(logging, level.upper()),
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    record.props = props
    log_func(record)
