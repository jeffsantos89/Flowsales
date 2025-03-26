import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class MarketplaceAPIThroughputTest:
    def __init__(self, base_url, endpoints, num_requests, num_threads):
        self.base_url = base_url
        self.endpoints = endpoints
        self.num_requests = num_requests
        self.num_threads = num_threads
        self.results = []

    def _make_request(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        start_time = time.time()
        try:
            response = requests.get(url)
            latency = time.time() - start_time
            return {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'latency': latency,
                'success': response.status_code == 200
            }
        except requests.RequestException as e:
            return {
                'endpoint': endpoint,
                'status_code': None,
                'latency': None,
                'success': False,
                'error': str(e)
            }

    def run_test(self):
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []
            for _ in range(self.num_requests):
                for endpoint in self.endpoints:
                    futures.append(executor.submit(self._make_request, endpoint))
            
            for future in as_completed(futures):
                self.results.append(future.result())

    def get_results(self):
        return self.results

    def print_summary(self):
        total_requests = len(self.results)
        successful_requests = sum(1 for result in self.results if result['success'])
        failed_requests = total_requests - successful_requests
        avg_latency = sum(result['latency'] for result in self.results if result['latency'] is not None) / successful_requests

        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Failed Requests: {failed_requests}")
        print(f"Average Latency: {avg_latency:.2f} seconds")

if __name__ == "__main__":
    base_url = "https://api.marketplace.com"
    endpoints = ["products", "orders", "users"]
    num_requests = 100
    num_threads = 10

    test = MarketplaceAPIThroughputTest(base_url, endpoints, num_requests, num_threads)
    test.run_test()
    test.print_summary()