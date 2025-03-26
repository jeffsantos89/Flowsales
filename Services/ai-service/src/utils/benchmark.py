import time
import functools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def benchmark(func):
    """
    A decorator that logs the time a function takes to execute.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logging.info(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper

def benchmark_with_threshold(threshold):
    """
    A decorator factory that logs the time a function takes to execute
    and warns if it exceeds a given threshold.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            if elapsed_time > threshold:
                logging.warning(f"Function '{func.__name__}' exceeded threshold with {elapsed_time:.4f} seconds")
            else:
                logging.info(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
            return result
        return wrapper
    return decorator

def benchmark_with_logging(logger):
    """
    A decorator factory that logs the time a function takes to execute
    using a custom logger.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            logger.info(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
            return result
        return wrapper
    return decorator

# Example usage
if __name__ == "__main__":
    @benchmark
    def example_function():
        time.sleep(1)

    example_function()