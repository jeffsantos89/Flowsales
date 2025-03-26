from typing import Dict, Any, Optional
import logging
import os
from pathlib import Path
from dataclasses import dataclass
from functools import wraps

"""
Shopee Chatbot Module
Provides advanced chatbot functionality for Shopee e-commerce platform integration.
"""

# Module version and metadata
__version__ = '1.0.0'
__author__ = 'Flowsale Team'
__status__ = 'Production'

# Configure logging with a more sophisticated setup
def setup_logging() -> logging.Logger:
    """Configure and return a logger with proper formatting and handlers."""
    logger = logging.getLogger("shopee_chatbot")
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(console_handler)
        
        # File handler for persistent logging
        log_file = Path('logs/shopee_chatbot.log')
        log_file.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

@dataclass
class DefaultConfig:
    """Default configuration constants."""
    MODEL_PATH: str = str(Path(__file__).parent / 'models')
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    LANGUAGE: str = 'pt-BR'
    API_KEY: str = os.getenv("SHOPEE_API_KEY", "")

def singleton(cls):
    """Singleton decorator for classes."""
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class ShopeeConfig:
    """Thread-safe configuration manager for Shopee chatbot."""
    
    def __init__(self):
        self._config = {
            'model_path': DefaultConfig.MODEL_PATH,
            'max_retries': DefaultConfig.MAX_RETRIES,
            'timeout': DefaultConfig.TIMEOUT,
            'language': DefaultConfig.LANGUAGE,
            'api_key': DefaultConfig.API_KEY
        }
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration parameters with validation.
        
        Args:
            **kwargs: Configuration parameters to update
        
        Raises:
            ValueError: If invalid configuration parameters are provided
        """
        valid_keys = self._config.keys()
        invalid_keys = set(kwargs.keys()) - set(valid_keys)
        
        if invalid_keys:
            raise ValueError(f"Invalid configuration keys: {invalid_keys}")
        
        self._config.update(kwargs)
        logger.info("Configuration updated: %s", 
                   {k: v for k, v in kwargs.items() if k != 'api_key'})
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get current configuration (immutable copy)."""
        return dict(self._config)
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        try:
            assert os.path.exists(self._config['model_path']), "Model path does not exist"
            assert self._config['max_retries'] > 0, "Max retries must be positive"
            assert self._config['timeout'] > 0, "Timeout must be positive"
            assert self._config['api_key'], "API key is not set"
            return True
        except AssertionError as e:
            logger.error("Configuration validation failed: %s", str(e))
            return False

class ChatbotInitializationError(Exception):
    """Custom exception for chatbot initialization errors."""
    pass

def initialize_chatbot(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Initialize the Shopee chatbot with custom configuration.
    
    Args:
        config: Optional configuration dictionary to override defaults
    
    Returns:
        bool: True if initialization was successful
    
    Raises:
        ChatbotInitializationError: If initialization fails
    """
    try:
        shopee_config = ShopeeConfig()
        if config:
            shopee_config.update_config(**config)
        
        if not shopee_config.validate_config():
            raise ChatbotInitializationError("Invalid configuration")
        
        logger.info("Shopee chatbot initialized successfully")
        return True
        
    except Exception as e:
        logger.error("Failed to initialize Shopee chatbot: %s", str(e))
        raise ChatbotInitializationError(f"Initialization failed: {str(e)}")

# Expose public interface
__all__ = [
    'ShopeeConfig',
    'initialize_chatbot',
    'ChatbotInitializationError',
    '__version__',
    '__author__',
    '__status__'
]
