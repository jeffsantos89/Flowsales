import time
import logging
import random
from functools import wraps
from typing import Tuple, Union, Callable, TypeVar, Any

# Type hints
T = TypeVar('T')
ExceptionTypes = Union[Tuple[type[Exception], ...], type[Exception]]

# Configure logging
logger = logging.getLogger("retry")

class RetryExhausted(Exception):
    """Custom exception for when all retry attempts are exhausted."""
    pass

def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: ExceptionTypes = (Exception,),
    on_retry: Callable[[Exception, int], None] = None
) -> Callable:
    """
    Advanced retry decorator with exponential backoff and jitter.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delay
        exceptions: Tuple of exceptions to catch
        on_retry: Optional callback function called on each retry
    """
    
    def calculate_delay(attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = min(initial_delay * (exponential_base ** attempt), max_delay)
        if jitter:
            delay *= (0.5 + random.random())
        return delay

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"All {max_attempts} retry attempts failed for {func.__name__}",
                            exc_info=True
                        )
                        raise RetryExhausted(
                            f"Failed after {max_attempts} attempts"
                        ) from e
                    
                    delay = calculate_delay(attempt)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}. "
                        f"Retrying in {delay:.2f}s. Error: {str(e)}"
                    )
                    
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.error(
                                f"Error in retry callback: {callback_error}",
                                exc_info=True
                            )
                    
                    time.sleep(delay)
            
            # This should never be reached due to the raise in the loop
            raise RetryExhausted("Unexpected retry failure")
            
        return wrapper
    return decorator
