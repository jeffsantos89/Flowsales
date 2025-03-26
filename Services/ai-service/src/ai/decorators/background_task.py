# src/ai/decorators/background_task.py

import threading
import functools
import queue
import logging
import time
from typing import Any, Callable, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskStatus:
    """Classe para armazenar o status da tarefa em background"""
    id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None

class BackgroundTaskManager:
    """Gerenciador de tarefas em background"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.task_queue = queue.Queue()
        self.task_status = {}
        self.max_workers = 5  # Configurável
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._start_monitor()

    def _start_monitor(self):
        """Inicia o monitor de tarefas em background"""
        def monitor():
            while True:
                self._cleanup_old_tasks()
                time.sleep(300)  # Limpa tarefas antigas a cada 5 minutos

        threading.Thread(target=monitor, daemon=True).start()

    def _cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tarefas antigas do histórico"""
        current_time = datetime.now()
        with self._lock:
            for task_id in list(self.task_status.keys()):
                task = self.task_status[task_id]
                age = (current_time - task.start_time).total_seconds() / 3600
                if age > max_age_hours:
                    del self.task_status[task_id]

    def add_task(self, task_id: str, func: Callable, *args, **kwargs) -> Dict:
        """Adiciona uma nova tarefa ao gerenciador"""
        task_status = TaskStatus(
            id=task_id,
            status="PENDING",
            start_time=datetime.now()
        )
        self.task_status[task_id] = task_status

        def task_wrapper():
            try:
                task_status.status = "RUNNING"
                result = func(*args, **kwargs)
                task_status.result = result
                task_status.status = "COMPLETED"
            except Exception as e:
                logger.exception(f"Error in background task {task_id}")
                task_status.status = "FAILED"
                task_status.error = str(e)
            finally:
                task_status.end_time = datetime.now()

        self.executor.submit(task_wrapper)
        return {"task_id": task_id, "status": "PENDING"}

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Retorna o status atual de uma tarefa"""
        task = self.task_status.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.id,
            "status": task.status,
            "start_time": task.start_time.isoformat(),
            "end_time": task.end_time.isoformat() if task.end_time else None,
            "result": task.result,
            "error": task.error
        }

def background_task(func: Callable) -> Callable:
    """Decorador para executar funções em background"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        task_id = f"{func.__name__}_{time.time()}"
        manager = BackgroundTaskManager()
        return manager.add_task(task_id, func, *args, **kwargs)
    return wrapper
