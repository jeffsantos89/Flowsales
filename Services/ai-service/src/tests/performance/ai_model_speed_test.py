import time
import logging
import statistics
from typing import List, Dict, Any, Callable
from datetime import datetime
import json
import numpy as np
from pathlib import Path
import pytest
from dataclasses import dataclass
from abc import ABC, abstractmethod

import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Data class to store performance metrics"""
    average_latency: float
    throughput: float
    p50_latency: float
    p90_latency: float
    p95_latency: float
    p99_latency: float
    total_requests: int
    failed_requests: int
    success_rate: float

class BaseModelTest(ABC):
    """Abstract base class for model testing"""
    
    @abstractmethod
    def setup(self) -> None:
        """Setup the model and resources"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    @abstractmethod
    def run_inference(self, input_data: Any) -> Any:
        """Run model inference"""
        pass

class AIModelSpeedTest(BaseModelTest):
    def __init__(self, model_name: str, batch_size: int = 1):
        self.model_name = model_name
        self.batch_size = batch_size
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        self.metrics: List[Dict[str, float]] = []

    def setup(self) -> None:
        """Initialize model and resources"""
        logger.info(f"Setting up test for model: {self.model_name}")
        # Add your model initialization here
        pass

    def cleanup(self) -> None:
        """Cleanup resources after test"""
        logger.info("Cleaning up resources")
        # Add cleanup logic here
        pass

    def run_inference(self, input_data: Any) -> Any:
        """Run single inference"""
        try:
            # Add your model inference logic here
            return {"result": "sample_output"}
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise

    def run_parallel_tests(self, 
                          test_data: List[Any], 
                          num_threads: int,
                          warmup_iterations: int = 10) -> PerformanceMetrics:
        """Run performance tests in parallel"""
        logger.info(f"Starting parallel tests with {num_threads} threads")
        
        def _single_test(input_data: Any) -> Dict[str, Any]:
            start_time = time.perf_counter()
            try:
                result = self.run_inference(input_data)
                success = True
            except Exception as e:
                result = str(e)
                success = False
            end_time = time.perf_counter()
            return {
                "latency": end_time - start_time,
                "success": success,
                "result": result
            }

        # Warmup phase
        logger.info("Running warmup iterations...")
        for _ in range(warmup_iterations):
            self.run_inference(test_data[0])

        # Main test phase
        latencies = []
        failed_requests = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_data = {executor.submit(_single_test, data): data 
                            for data in test_data}
            
            for future in concurrent.futures.as_completed(future_to_data):
                result = future.result()
                latencies.append(result["latency"])
                if not result["success"]:
                    failed_requests += 1

        # Calculate metrics
        total_time = sum(latencies)
        total_requests = len(test_data)
        
        metrics = PerformanceMetrics(
            average_latency=statistics.mean(latencies),
            throughput=total_requests / total_time,
            p50_latency=np.percentile(latencies, 50),
            p90_latency=np.percentile(latencies, 90),
            p95_latency=np.percentile(latencies, 95),
            p99_latency=np.percentile(latencies, 99),
            total_requests=total_requests,
            failed_requests=failed_requests,
            success_rate=(total_requests - failed_requests) / total_requests * 100
        )

        self._save_results(metrics)
        return metrics

    def _save_results(self, metrics: PerformanceMetrics) -> None:
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = self.results_dir / f"test_results_{self.model_name}_{timestamp}.json"
        
        results = {
            "model_name": self.model_name,
            "timestamp": timestamp,
            "batch_size": self.batch_size,
            "metrics": {
                "average_latency_ms": metrics.average_latency * 1000,
                "throughput_rps": metrics.throughput,
                "p50_latency_ms": metrics.p50_latency * 1000,
                "p90_latency_ms": metrics.p90_latency * 1000,
                "p95_latency_ms": metrics.p95_latency * 1000,
                "p99_latency_ms": metrics.p99_latency * 1000,
                "total_requests": metrics.total_requests,
                "failed_requests": metrics.failed_requests,
                "success_rate": metrics.success_rate
            }
        }

        with open(result_file, 'w') as f:
            json.dump(results, f, indent=4)
        logger.info(f"Results saved to {result_file}")

@pytest.fixture
def model_test():
    test = AIModelSpeedTest(model_name="test_model")
    test.setup()
    yield test
    test.cleanup()

def test_model_performance(model_test):
    """Example test function"""
    test_data = [{"input": f"test_{i}"} for i in range(100)]
    metrics = model_test.run_parallel_tests(
        test_data=test_data,
        num_threads=4,
        warmup_iterations=10
    )
    
    # Assert performance requirements
    assert metrics.average_latency < 1.0, "Average latency too high"
    assert metrics.success_rate > 99.0, "Success rate too low"
    assert metrics.throughput > 10.0, "Throughput too low"

if __name__ == "__main__":
    pytest.main([__file__])