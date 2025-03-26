import time
import unittest
import tracemalloc

from ai_service import AiService  # Import your AI service module

class PerformanceTestAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ai_service = AiService()
        cls.test_data = cls._generate_test_data()

    @staticmethod
    def _generate_test_data():
        # Generate or load test data
        return ["sample data 1", "sample data 2", "sample data 3"]

    def test_response_time(self):
        max_response_time = 1.0  # seconds
        for data in self.test_data:
            start_time = time.time()
            response = self.ai_service.process(data)
            end_time = time.time()
            response_time = end_time - start_time
            self.assertLessEqual(response_time, max_response_time, f"Response time {response_time} exceeded {max_response_time} seconds")

    def test_memory_usage(self):
        tracemalloc.start()
        for data in self.test_data:
            self.ai_service.process(data)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        max_memory_usage = 50 * 1024 * 1024  # 50 MB
        self.assertLessEqual(peak, max_memory_usage, f"Memory usage {peak} exceeded {max_memory_usage} bytes")

    def test_scalability(self):
        import concurrent.futures
        max_workers = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.ai_service.process, data) for data in self.test_data * max_workers]
            for future in concurrent.futures.as_completed(futures):
                self.assertIsNotNone(future.result())

    def test_accuracy(self):
        expected_results = ["expected result 1", "expected result 2", "expected result 3"]
        for data, expected in zip(self.test_data, expected_results):
            result = self.ai_service.process(data)
            self.assertEqual(result, expected, f"Expected {expected} but got {result}")

if __name__ == '__main__':
    unittest.main()