import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar('T')

def async_retry(retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator to retry an async function if it raises specified exceptions.

    :param retries: Number of retries before giving up.
    :param delay: Delay between retries in seconds.
    :param exceptions: Tuple of exception classes to catch and retry.
    :return: Wrapped function with retry logic.
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            attempt = 0
            while attempt < retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= retries:
                        raise
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

async def gather_with_concurrency(n: int, *tasks: Coroutine) -> Any:
    """
    Run tasks with a specified concurrency limit.

    :param n: Maximum number of concurrent tasks.
    :param tasks: Coroutine tasks to run.
    :return: Results of the tasks.
    """
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task: Coroutine) -> Any:
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))

def run_sync(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """
    Run an async function synchronously.

    :param func: Async function to run.
    :return: Synchronous wrapper of the async function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        return asyncio.run(func(*args, **kwargs))
    return wrapper