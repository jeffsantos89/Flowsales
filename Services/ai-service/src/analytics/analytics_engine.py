"""
Analytics Engine Module
Provides data processing capabilities for user analytics.
"""

import logging
from typing import Any, Optional
from importlib import import_module
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnalyticsEngineError(Exception):
    """Custom exception for Analytics Engine related errors."""
    pass

@lru_cache(maxsize=1)
def get_processor():
    """
    Cached loader for the analytics processor.
    Returns the process_user_data function.
    """
    try:
        analytics_module = import_module('analytics_engine')
        return getattr(analytics_module, 'process_user_data')
    except ImportError as e:
        logger.error(f"Critical: Failed to import process_user_data: {str(e)}")
        raise AnalyticsEngineError(f"Analytics engine initialization failed: {str(e)}") from e
    except AttributeError as e:
        logger.error(f"Critical: process_user_data not found in module: {str(e)}")
        raise AnalyticsEngineError("process_user_data function not found") from e

def process_user_data(*args: Any, **kwargs: Any) -> Optional[Any]:
    """
    Wrapper function for processing user data with error handling.
    
    Args:
        *args: Positional arguments to pass to the processor
        **kwargs: Keyword arguments to pass to the processor
        
    Returns:
        Processing result or None if processing fails
    """
    try:
        processor = get_processor()
        return processor(*args, **kwargs)
    except Exception as e:
        logger.exception(f"Error processing user data: {str(e)}")
        raise AnalyticsEngineError(f"Data processing failed: {str(e)}") from e

__all__ = ['process_user_data', 'AnalyticsEngineError']