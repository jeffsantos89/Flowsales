"""
__init__.py
Initialize the LinkedIn module with advanced configuration, logging, and error handling.
"""

import os
import logging.config
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import yaml
import dotenv
from functools import lru_cache

@dataclass
class LinkedInConfig:
    """Configuration class for LinkedIn settings"""
    api_key: str
    environment: str
    retry_attempts: int = 3
    timeout: int = 30
    cache_ttl: int = 3600

class LinkedInModuleError(Exception):
    """Base exception for LinkedIn module"""
    pass

class ConfigurationError(LinkedInModuleError):
    """Raised when there's a configuration error"""
    pass

@lru_cache()
def load_config() -> LinkedInConfig:
    """
    Load configuration from environment variables and config files.
    Cached to avoid repeated disk reads.
    """
    # Load .env file if exists
    dotenv.load_dotenv()
    
    try:
        config_path = Path(__file__).parent / "config" / f"{os.getenv('ENV', 'development')}.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
        else:
            config_data = {}

        return LinkedInConfig(
            api_key=os.getenv("LINKEDIN_API_KEY") or config_data.get("api_key"),
            environment=os.getenv("ENV", "development"),
            retry_attempts=int(os.getenv("LINKEDIN_RETRY_ATTEMPTS", config_data.get("retry_attempts", 3))),
            timeout=int(os.getenv("LINKEDIN_TIMEOUT", config_data.get("timeout", 30))),
            cache_ttl=int(os.getenv("LINKEDIN_CACHE_TTL", config_data.get("cache_ttl", 3600)))
        )
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {str(e)}")

def setup_logging() -> None:
    """Configure logging with advanced settings"""
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s | %(name)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'detailed',
                'level': 'INFO'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'linkedin_module.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'detailed',
                'level': 'DEBUG'
            }
        },
        'loggers': {
            'linkedin': {
                'handlers': ['console', 'file'],
                'level': os.getenv('LINKEDIN_LOG_LEVEL', 'INFO'),
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(logging_config)

logger = logging.getLogger('linkedin')

def initialize_linkedin_module() -> None:
    """
    Initialize the LinkedIn module with error handling and validation.
    """
    try:
        setup_logging()
        config = load_config()
        
        if not config.api_key:
            raise ConfigurationError("LinkedIn API key not configured")
            
        logger.info(f"[LinkedIn] Module initialized in {config.environment} environment")
        logger.debug(f"[LinkedIn] Configuration loaded: {config}")
        
    except Exception as e:
        logger.error(f"[LinkedIn] Failed to initialize module: {str(e)}")
        raise LinkedInModuleError(f"Module initialization failed: {str(e)}")

# Initialize module when imported
try:
    initialize_linkedin_module()
except Exception as e:
    logger.critical(f"Critical error during module initialization: {str(e)}")
    raise
