"""
Configuration Management Module for Flowsale Platform

This module provides a centralized configuration management system that handles:
- Application settings
- Security policies and authentication
- API rate limiting
- Feature flags
- Secrets management
- Environment variables
- Logging configuration

The module implements singleton patterns and lazy loading to optimize resource usage.
"""

from typing import List, Any
from functools import lru_cache
import logging.config
from contextlib import contextmanager

# Core configuration components
from settings import settings
from secrets import secrets_manager
from env_loader import env_loader
from api_limits import api_limits
from feature_flags import feature_manager
from security_policies import security_policies
from logging_config import setup_logging

# Version control
__version__ = '1.0.0'

# Module initialization status
_initialized = False

@lru_cache(maxsize=1)
def initialize_config() -> None:
    """
    Initialize all configuration components in the correct order with error handling.
    Uses lru_cache to ensure single initialization.
    """
    global _initialized
    if _initialized:
        return

    try:
        # Order matters - initialize components with dependencies first
        env_loader.load()
        setup_logging()
        secrets_manager.initialize()
        settings.validate()
        api_limits.configure()
        feature_manager.load_features()
        security_policies.configure()
        
        _initialized = True
        
        logging.info("Configuration system initialized successfully")
    except Exception as e:
        logging.critical(f"Failed to initialize configuration system: {str(e)}")
        raise RuntimeError("Configuration initialization failed") from e

@contextmanager
def config_context():
    """Context manager for configuration handling"""
    initialize_config()
    try:
        yield
    finally:
        # Cleanup if needed
        pass

# Public exports
__all__: List[str] = [
    "settings",
    "secrets_manager", 
    "env_loader",
    "api_limits",
    "feature_manager",
    "security_policies",
    "setup_logging",
    "initialize_config",
    "config_context"
]

def get_component(name: str) -> Any:
    """
    Safely get a configuration component by name.
    
    Args:
        name: The name of the component to retrieve
        
    Returns:
        The requested configuration component
        
    Raises:
        ValueError: If component name is invalid
    """
    if name not in __all__:
        raise ValueError(f"Invalid configuration component: {name}")
    return globals()[name]