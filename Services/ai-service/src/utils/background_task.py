import threading
from functools import wraps
import logging
from typing import Any, Callable
from concurrent.futures import Future
from queue import Queue
import traceback

logger = logging.getLogger("background")

class BackgroundTaskManager:
    _instance = None
    _tasks: Queue = Queue()
    _max_workers: int = 5
    _workers: list[threading.Thread] = []

    @classmethod
    def get_instance(cls) -> 'BackgroundTaskManager':
        if cls._instance is None:
            cls._instance = BackgroundTaskManager()
        return cls._instance

    def __init__(self):
        self._start_workers()

    def _start_workers(self):
        for _ in range(self._max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self._workers.append(worker)

    def _worker_loop(self):
        while True:
            func, args, kwargs, future = self._tasks.get()
            try:
                result = func(*args, **kwargs)
                if future:
                    future.set_result(result)
            except Exception as e:
                logger.exception(f"Error in background task: {e}")
                if future:
                    future.set_exception(e)
            finally:
                self._tasks.task_done()

def background_task(func: Callable[..., Any]) -> Callable[..., Future]:
    """
    Decorator to run function in parallel thread with error handling and task management.
    Returns a Future object that can be used to check task status and get results.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Future:
        future = Future()
        task_manager = BackgroundTaskManager.get_instance()
        task_manager._tasks.put((func, args, kwargs, future))
        return future
    return wrapper
