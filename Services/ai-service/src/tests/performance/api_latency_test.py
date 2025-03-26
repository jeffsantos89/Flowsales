import aiohttp
import asyncio
import logging
import time
import statistics
import json
from datetime import datetime
from typing import Dict, List, Any
import pytest
from dataclasses import dataclass
import numpy as np
from pathlib import Path

import matplotlib.pyplot as plt

# Configuration for the test
@dataclass
class TestConfig:
    base_url: str = "http://localhost:8000"  # Replace with your API endpoint
    endpoints: List[str] = None
    num_requests: int = 1000
    concurrent_users: int = 50
    timeout_seconds: int = 30
    log_file: str = "api_latency_test.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_latency_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APILatencyTest:
    def __init__(self, config: TestConfig):
        self.config = config
        self.results: Dict[str, List[float]] = {}
        self.errors: Dict[str, List[str]] = {}
        
        if not self.config.endpoints:
            self.config.endpoints = [
                "/api/v1/predict",
                "/api/v1/health",
                # Add more endpoints as needed
            ]

    async def make_request(self, session: aiohttp.ClientSession, endpoint: str) -> Dict[str, Any]:
        start_time = time.time()
        try:
            async with session.get(
                f"{self.config.base_url}{endpoint}",
                timeout=self.config.timeout_seconds
            ) as response:
                await response.text()
                latency = time.time() - start_time
                return {"success": True, "latency": latency, "status": response.status}
        except Exception as e:
            return {"success": False, "error": str(e), "latency": time.time() - start_time}

    async def run_concurrent_requests(self, endpoint: str) -> None:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(self.config.num_requests):
                tasks.append(self.make_request(session, endpoint))
            
            results = await asyncio.gather(*tasks)
            
            self.results[endpoint] = []
            self.errors[endpoint] = []
            
            for result in results:
                if result["success"]:
                    self.results[endpoint].append(result["latency"])
                else:
                    self.errors[endpoint].append(result["error"])

    def calculate_statistics(self, endpoint: str) -> Dict[str, float]:
        latencies = self.results[endpoint]
        return {
            "min": min(latencies) * 1000,  # Convert to ms
            "max": max(latencies) * 1000,
            "mean": statistics.mean(latencies) * 1000,
            "median": statistics.median(latencies) * 1000,
            "p95": np.percentile(latencies, 95) * 1000,
            "p99": np.percentile(latencies, 99) * 1000,
            "std_dev": statistics.stdev(latencies) * 1000 if len(latencies) > 1 else 0
        }

    def generate_report(self) -> None:
        report = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config.__dict__,
            "results": {},
            "errors": self.errors
        }

        for endpoint in self.config.endpoints:
            if endpoint in self.results:
                report["results"][endpoint] = self.calculate_statistics(endpoint)

        # Save report to JSON
        report_path = Path("reports") / f"latency_report_{int(time.time())}.json"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Generate plots
        self.generate_plots()

    def generate_plots(self) -> None:
        plots_dir = Path("reports/plots")
        plots_dir.mkdir(exist_ok=True, parents=True)

        for endpoint, latencies in self.results.items():
            plt.figure(figsize=(10, 6))
            plt.hist(latencies, bins=50)
            plt.title(f"Latency Distribution - {endpoint}")
            plt.xlabel("Latency (seconds)")
            plt.ylabel("Frequency")
            plt.savefig(plots_dir / f"latency_dist_{endpoint.replace('/', '_')}.png")
            plt.close()

@pytest.mark.asyncio
async def test_api_latency():
    """Main test function that can be run with pytest"""
    config = TestConfig()
    tester = APILatencyTest(config)
    
    for endpoint in config.endpoints:
        logger.info(f"Testing endpoint: {endpoint}")
        await tester.run_concurrent_requests(endpoint)
        
        stats = tester.calculate_statistics(endpoint)
        logger.info(f"Results for {endpoint}:")
        logger.info(f"P95 Latency: {stats['p95']:.2f}ms")
        logger.info(f"Mean Latency: {stats['mean']:.2f}ms")
        
        # Assert performance requirements
        assert stats['p95'] < 1000, f"P95 latency exceeds 1000ms for {endpoint}"
        assert stats['mean'] < 500, f"Mean latency exceeds 500ms for {endpoint}"

    tester.generate_report()

if __name__ == "__main__":
    asyncio.run(test_api_latency())