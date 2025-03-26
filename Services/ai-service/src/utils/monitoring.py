import time
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Monitoring:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()
        logger.info("Monitoring started.")

    def stop(self):
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        logger.info(f"Monitoring stopped. Elapsed time: {elapsed_time:.2f} seconds.")
        return elapsed_time

    def log_performance(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting execution of {func.__name__}")
            self.start()
            result = func(*args, **kwargs)
            elapsed_time = self.stop()
            logger.info(f"Finished execution of {func.__name__} in {elapsed_time:.2f} seconds.")
            return result
        return wrapper

# Example usage
monitoring = Monitoring()

@monitoring.log_performance
def example_function():
    time.sleep(2)
    return "Function completed."

if __name__ == "__main__":
    result = example_function()
    logger.info(result)