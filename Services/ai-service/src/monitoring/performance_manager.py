import logging
from typing import Any, Optional, Dict, Generator
from dataclasses import dataclass
from functools import lru_cache
from contextlib import contextmanager
import json

from performance_manager import PerformanceManager
from exceptions import PerformanceException

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ResourceMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float

class PerformanceException(Exception):
    """Exception raised for performance-related errors."""
    pass

class EnhancedPerformanceManager:
    def __init__(self, config_path: str = "config/performance_config.json"):
        self.performance = PerformanceManager()
        self.config = self._load_config(config_path)
        self.cache = {}
    
    @staticmethod
    def _load_config(config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return {}

    @contextmanager
    def monitor_resources(self) -> Generator[ResourceMetrics, None, None]:
        """Monitor system resources with context manager"""
        try:
            metrics_start = self.performance.monitor_resources()
            yield metrics_start
        finally:
            metrics_end = self.performance.monitor_resources()
            logger.info(f"Resource usage delta: {metrics_end - metrics_start}")

    def profile(self, save_to_file: bool = True, output_dir: str = "profiles/"):
        """Decorator for profiling functions"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    with self.monitor_resources():
                        result = self.performance.profile(
                            func, 
                            save_to_file=save_to_file,
                            output_dir=output_dir
                        )(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(f"Profiling failed: {str(e)}")
                    raise PerformanceException(f"Profiling error: {str(e)}")
            return wrapper
        return decorator

    @lru_cache(maxsize=128)
    def optimize_model(self, model_instance: Any, config_override: Optional[Dict] = None) -> Any:
        """Optimize model with caching"""
        try:
            config = {**self.config, **(config_override or {})}
            return self.performance.optimize_model(model_instance, config=config)
        except Exception as e:
            logger.error(f"Model optimization failed: {str(e)}")
            raise PerformanceException(f"Optimization error: {str(e)}")

    def choose_best_node(self, criteria: Optional[Dict] = None) -> str:
        """Choose best execution node with custom criteria"""
        try:
            default_criteria = self.config.get('node_selection_criteria', {})
            final_criteria = {**default_criteria, **(criteria or {})}
            return self.performance.choose_best_node(criteria=final_criteria)
        except Exception as e:
            logger.error(f"Node selection failed: {str(e)}")
            raise PerformanceException(f"Node selection error: {str(e)}")

    def clear_cache(self, cache_key: str) -> bool:
        """Clear specific cache with validation"""
        try:
            if not cache_key:
                raise ValueError("Cache key cannot be empty")
            return self.performance.clear_cache(cache_key)
        except Exception as e:
            logger.error(f"Cache clearing failed: {str(e)}")
            return False

    def optimize_query(self, **kwargs) -> Any:
        """Optimize database query with safety checks"""
        try:
            if 'min_amount' in kwargs and kwargs['min_amount'] < 0:
                raise ValueError("min_amount cannot be negative")
            return self.performance.optimize_query(**kwargs)
        except Exception as e:
            logger.error(f"Query optimization failed: {str(e)}")
            raise PerformanceException(f"Query optimization error: {str(e)}")

# Exemplo de uso
if __name__ == "__main__":
    perf_manager = EnhancedPerformanceManager()
    
    # Monitoramento de recursos
    with perf_manager.monitor_resources() as metrics:
        logger.info(f"Current metrics: {metrics}")
    
    # Exemplo de função com profile
    @perf_manager.profile(save_to_file=True)
    def example_function(x: int) -> int:
        return x * 2
