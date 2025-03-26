from typing import Dict, Any, Optional
import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from datetime import datetime
from functools import wraps
from pathlib import Path

"""
Telegram Chatbots Module
Provides enterprise-grade implementation for Telegram bot interactions and management.
"""

__version__ = '1.0.0'
__author__ = 'Flowsale Team'

class SingletonMeta(type):
    """Metaclass for implementing Singleton pattern"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class TelegramBotConfig(metaclass=SingletonMeta):
    """Enterprise-grade configuration management for Telegram bots"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._initialized: bool = False
        self._environment: str = os.getenv('ENV', 'development')
        
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize bot configuration with validation"""
        required_keys = {'bot_token', 'api_base_url', 'webhook_url'}
        if not all(key in config for key in required_keys):
            raise ValueError(f"Missing required configuration keys: {required_keys - set(config.keys())}")
        
        self._config = config
        self._initialized = True
        logger.info("TelegramBotConfig initialized successfully")
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    @property
    def environment(self) -> str:
        return self._environment
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Safely get configuration value with logging"""
        if not self._initialized:
            raise RuntimeError("Configuration not initialized")
        
        value = self._config.get(key, default)
        if value is None and default is None:
            logger.warning(f"Requested configuration key '{key}' not found")
        return value

    def validate_configuration(self) -> bool:
        """Validate current configuration state"""
        try:
            required_keys = {'bot_token', 'api_base_url', 'webhook_url'}
            return all(self.get_config(key) for key in required_keys)
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            return False

class LoggingManager:
    """Centralized logging management"""
    
    @staticmethod
    def setup_logging(
        log_level: int = logging.INFO,
        log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ) -> None:
        """Configure module logging with enhanced features"""
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'telegram_bot.log'
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Set formatter for both handlers
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logger.info(f"Logging setup completed at {datetime.utcnow().isoformat()}")

def require_initialization(func):
    """Decorator to ensure configuration is initialized before function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not bot_config.is_initialized:
            raise RuntimeError("Bot configuration must be initialized first")
        return func(*args, **kwargs)
    return wrapper

# Initialize global configuration and logging
bot_config = TelegramBotConfig()
logger = logging.getLogger(__name__)
LoggingManager.setup_logging()

def initialize_telegram_module(config: Dict[str, Any]) -> None:
    """Initialize the Telegram module with provided configuration"""
    try:
        bot_config.initialize(config)
        if bot_config.validate_configuration():
            logger.info(f"[Telegram] Module initialized successfully in {bot_config.environment} environment")
        else:
            raise ValueError("Configuration validation failed")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram module: {str(e)}")
        raise

__all__ = ['TelegramBotConfig', 'bot_config', 'initialize_telegram_module']
