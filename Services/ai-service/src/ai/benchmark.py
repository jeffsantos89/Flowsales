import time
import logging
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from ml_models.model_registry import ModelRegistry
from quantum.optimizations.quantum_machine_learning import QuantumML

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    model_name: str
    inference_times: List[float]
    mean_time: float
    std_dev: float
    total_runs: int

class ModelBenchmark:
    def __init__(self, num_runs: int = 100, parallel_executions: int = 4):
        self.num_runs = num_runs
        self.parallel_executions = parallel_executions
        self.model_registry = ModelRegistry()
        self.quantum_ml = QuantumML()
        self.results: Dict[str, BenchmarkResult] = {}

    def _run_ml_inference(self) -> float:
        """Execute single ML model inference and return execution time"""
        try:
            start_time = time.perf_counter()
            ml_model = self.model_registry.load_model("ml_model_v1")
            ml_model.predict([[0.5, 0.2, 0.8]])
            return time.perf_counter() - start_time
        except Exception as e:
            logger.error(f"ML inference failed: {str(e)}")
            raise

    def _run_quantum_inference(self) -> float:
        """Execute single quantum model inference and return execution time"""
        try:
            start_time = time.perf_counter()
            self.quantum_ml.build_model()
            return time.perf_counter() - start_time
        except Exception as e:
            logger.error(f"Quantum inference failed: {str(e)}")
            raise

    def _calculate_statistics(self, times: List[float]) -> tuple:
        """Calculate mean and standard deviation of execution times"""
        mean_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        return mean_time, std_dev

    def benchmark_model(self, model_type: str) -> BenchmarkResult:
        """Run benchmark for specified model type"""
        inference_times = []
        inference_func = (self._run_ml_inference if model_type == "ml" 
                         else self._run_quantum_inference)

        with ThreadPoolExecutor(max_workers=self.parallel_executions) as executor:
            futures = [executor.submit(inference_func) for _ in range(self.num_runs)]
            for future in futures:
                try:
                    inference_times.append(future.result())
                except Exception as e:
                    logger.error(f"Benchmark failed for {model_type}: {str(e)}")

        mean_time, std_dev = self._calculate_statistics(inference_times)
        return BenchmarkResult(
            model_name=model_type,
            inference_times=inference_times,
            mean_time=mean_time,
            std_dev=std_dev,
            total_runs=len(inference_times)
        )

    def run_benchmarks(self) -> Dict[str, BenchmarkResult]:
        """Run benchmarks for all models"""
        try:
            logger.info(f"Starting benchmarks with {self.num_runs} runs per model")
            
            for model_type in ["ml", "quantum"]:
                result = self.benchmark_model(model_type)
                self.results[model_type] = result
                
                logger.info(
                    f"{model_type.upper()} Model Results:\n"
                    f"Mean inference time: {result.mean_time:.4f} seconds\n"
                    f"Standard deviation: {result.std_dev:.4f} seconds\n"
                    f"Total successful runs: {result.total_runs}"
                )

            return self.results

        except Exception as e:
            logger.error(f"Benchmark failed: {str(e)}")
            raise

def main():
    try:
        benchmark = ModelBenchmark(num_runs=100, parallel_executions=4)
        benchmark.run_benchmarks()
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
