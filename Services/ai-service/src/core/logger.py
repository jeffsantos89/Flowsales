import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from typing import Optional, Dict, Any
from functools import wraps
import traceback

class CustomLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger('FlowsaleLogger')
            self.setup_logger()

    def setup_logger(self, log_level: str = 'INFO') -> None:
        """Configure the logger with both file and console handlers"""
        self.logger.setLevel(getattr(logging, log_level))

        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # File handler with rotation by size (10MB) keeping 30 backup files
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, 'flowsale.log'),
            maxBytes=10_000_000,  # 10MB
            backupCount=30,
            encoding='utf-8'
        )

        # Daily rotating file handler
        daily_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, 'flowsale_daily.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)

        # Create custom formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Set formatter for all handlers
        file_handler.setFormatter(formatter)
        daily_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(daily_handler)
        self.logger.addHandler(console_handler)

    def _log_message(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Internal method to handle logging with extra context"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message': message,
            'extra': extra or {}
        }
        
        log_func = getattr(self.logger, level.lower())
        log_func(json.dumps(log_data))

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self._log_message('INFO', message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self._log_message('ERROR', message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self._log_message('WARNING', message, extra)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self._log_message('DEBUG', message, extra)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self._log_message('CRITICAL', message, extra)

def log_exception(logger: CustomLogger):
    """Decorator to automatically log exceptions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_details = {
                    'exception_type': type(e).__name__,
                    'exception_message': str(e),
                    'traceback': traceback.format_exc()
                }
                logger.error(f"Exception in {func.__name__}", extra=error_details)
                raise
        return wrapper
    return decorator

# Global logger instance
logger = CustomLogger()

# Usage example:
if __name__ == '__main__':
    # Basic usage
    logger.info("Application started")
    
    # With extra context
    logger.info("User action", extra={'user_id': '123', 'action': 'login'})
    
    # Using the exception decorator
    @log_exception(logger)
    def sample_function():
        raise ValueError("Sample error")
    
    try:
        sample_function()
    except ValueError:
        pass