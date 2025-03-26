from typing import Dict, Any, Optional
import logging
from pathlib import Path
import sys
import importlib
from contextlib import contextmanager, asynccontextmanager
import atexit
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Set

"""
MercadoLivre Chatbot Module
Provides functionality for interacting with MercadoLivre's platform through chatbot interfaces.
"""

class Environment(Enum):
    """Supported environments for the chatbot"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"

@dataclass
class ChatbotConfig:
    """Configuration dataclass for type safety and validation"""
    api_key: str
    environment: Environment
    timeout: int
    max_retries: int = 3
    base_url: str = "https://api.mercadolibre.com"
    debug_mode: bool = False

class ChatbotException(Exception):
    """Base exception class for MercadoLivre chatbot module"""
    pass

class ConfigurationError(ChatbotException):
    """Raised when there's an error in configuration"""
    pass

class ChatbotState:
    """Singleton class to manage chatbot state"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatbotState, cls).__new__(cls)
            cls._instance._config = None
            cls._instance._initialized = False
            cls._instance._logger = None
        return cls._instance

    @property
    def config(self) -> Optional[ChatbotConfig]:
        return self._config

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def logger(self) -> logging.Logger:
        if not self._logger:
            self._setup_logging()
        return self._logger

    def _setup_logging(self) -> None:
        """Configure logging with advanced formatting"""
        log_format = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        self._logger = logging.getLogger("mercadolivre.chatbot")
        self._logger.setLevel(logging.INFO)
        
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(log_format, date_format))
            self._logger.addHandler(handler)

_state = ChatbotState()

def initialize_chatbot(config_dict: Dict[str, Any]) -> None:
    """
    Initialize the MercadoLivre chatbot module with the provided configuration.
    
    Args:
        config_dict: Dictionary containing configuration parameters
    
    Raises:
        ConfigurationError: If configuration is invalid or initialization fails
    """
    try:
        # Validate and create config object
        config = ChatbotConfig(
            api_key=config_dict.get('api_key') or os.getenv("MERCADO_LIBRE_API_KEY"),
            environment=Environment(config_dict.get('environment', 'development')),
            timeout=int(config_dict.get('timeout', 30)),
            max_retries=int(config_dict.get('max_retries', 3)),
            debug_mode=bool(config_dict.get('debug_mode', False))
        )
        
        # Verify dependencies
        _ensure_module_dependencies()
        
        # Update state
        _state._config = config
        _state._initialized = True
        
        _state.logger.info(f"MercadoLivre chatbot initialized in {config.environment.value} environment")
        
        if config.debug_mode:
            _state.logger.setLevel(logging.DEBUG)
            
    except Exception as e:
        _state.logger.error(f"Initialization failed: {str(e)}")
        raise ConfigurationError(f"Initialization failed: {str(e)}") from e

def get_chatbot_config() -> ChatbotConfig:
    """Get the current chatbot configuration."""
    if not _state.initialized:
        raise ChatbotException("Chatbot module not initialized")
    return _state.config

@asynccontextmanager
async def chatbot_session():
    """Async context manager for handling chatbot sessions"""
    if not _state.initialized:
        raise ChatbotException("Chatbot module not initialized")
    try:
        _state.logger.debug("Starting chatbot session")
        yield
    finally:
        _state.logger.debug("Closing chatbot session")

def _ensure_module_dependencies() -> None:
    """Verify that all required dependencies are available"""
    required_packages: Set[str] = {'requests', 'aiohttp', 'pydantic'}
    missing_packages = {
        package for package in required_packages
        if not _check_package(package)
    }
    
    if missing_packages:
        raise ImportError(f"Missing required packages: {', '.join(missing_packages)}")

def _check_package(package: str) -> bool:
    """Check if a package is installed"""
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False

@atexit.register
def _cleanup() -> None:
    """Cleanup handler for module resources"""
    if _state.initialized:
        _state._config = None
        _state._initialized = False
        _state.logger.info("MercadoLivre chatbot module cleaned up")

# Module version and metadata
__version__ = '1.1.0'
__author__ = 'Flowsale Team'
__all__ = ['initialize_chatbot', 'get_chatbot_config', 'ChatbotException', 
           'ChatbotConfig', 'Environment', 'chatbot_session']
