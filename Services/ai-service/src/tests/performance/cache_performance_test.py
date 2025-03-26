import time
import statistics
import unittest
import random
from functools import lru_cache
from typing import Any, Dict, List
from dataclasses import dataclass
import logging
from datetime import datetime

import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CachePerformanceMetrics:
    operation: str
    execution_time: float
    memory_usage: int
    hit_rate: float
    miss_rate: float
    sample_size: int

class MockCache:
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any:
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        if len(self.cache) >= self.max_size:
            # Simple LRU implementation
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value

    def clear(self) -> None:
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

    @property
    def miss_rate(self) -> float:
        return 1 - self.hit_rate

class CachePerformanceTest(unittest.TestCase):
    def setUp(self):
        self.cache = MockCache()
        self.sample_sizes = [100, 1000, 10000]
        self.results: List[CachePerformanceMetrics] = []

    def measure_execution_time(self, func) -> float:
        start_time = time.perf_counter()
        func()
        return time.perf_counter() - start_time

    def test_cache_write_performance(self):
        logger.info("Starting write performance test")
        
        for size in self.sample_sizes:
            def write_operation():
                for i in range(size):
                    key = f"key_{i}"
                    value = f"value_{i}"
                    self.cache.set(key, value)

            execution_time = self.measure_execution_time(write_operation)
            
            metrics = CachePerformanceMetrics(
                operation="write",
                execution_time=execution_time,
                memory_usage=len(self.cache.cache),
                hit_rate=self.cache.hit_rate,
                miss_rate=self.cache.miss_rate,
                sample_size=size
            )
            self.results.append(metrics)
            self.cache.clear()

    def test_cache_read_performance(self):
        logger.info("Starting read performance test")
        
        for size in self.sample_sizes:
            # Prepare cache with data
            for i in range(size):
                self.cache.set(f"key_{i}", f"value_{i}")

            def read_operation():
                for i in range(size):
                    self.cache.get(f"key_{random.randint(0, size-1)}")

            execution_time = self.measure_execution_time(read_operation)
            
            metrics = CachePerformanceMetrics(
                operation="read",
                execution_time=execution_time,
                memory_usage=len(self.cache.cache),
                hit_rate=self.cache.hit_rate,
                miss_rate=self.cache.miss_rate,
                sample_size=size
            )
            self.results.append(metrics)
            self.cache.clear()

    def test_concurrent_access(self):
        logger.info("Starting concurrent access test")
        size = 1000
        
        # Prepare cache with initial data
        for i in range(size):
            self.cache.set(f"key_{i}", f"value_{i}")

        def concurrent_operation():
            operation = random.choice(['read', 'write'])
            key = f"key_{random.randint(0, size-1)}"
            if operation == 'read':
                self.cache.get(key)
            else:
                self.cache.set(key, f"new_value_{random.randint(0, 1000)}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            start_time = time.perf_counter()
            futures = [executor.submit(concurrent_operation) for _ in range(size)]
            concurrent.futures.wait(futures)
            execution_time = time.perf_counter() - start_time

        metrics = CachePerformanceMetrics(
            operation="concurrent",
            execution_time=execution_time,
            memory_usage=len(self.cache.cache),
            hit_rate=self.cache.hit_rate,
            miss_rate=self.cache.miss_rate,
            sample_size=size
        )
        self.results.append(metrics)

    def tearDown(self):
        # Generate performance report
        logger.info("\nPerformance Test Results:")
        logger.info("-" * 80)
        
        for metric in self.results:
            logger.info(f"""
Operation: {metric.operation}
Sample Size: {metric.sample_size}
Execution Time: {metric.execution_time:.4f} seconds
Memory Usage: {metric.memory_usage} items
Hit Rate: {metric.hit_rate:.2%}
Miss Rate: {metric.miss_rate:.2%}
            """)

if __name__ == '__main__':
    unittest.main(verbosity=2)