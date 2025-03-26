import cProfile
import pstats
import io
import functools
import logging
import time
from typing import Callable, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ProfilingError(Exception):
    """Custom exception for profiling errors"""
    pass

def profile_function(
    output_dir: Optional[str] = None,
    save_stats: bool = False,
    print_output: bool = True,
    sort_by: str = "cumulative",
    lines_to_print: int = 20
) -> Callable:
    """
    Advanced profiling decorator that can save results to files and handle errors gracefully.
    
    Args:
        output_dir: Directory to save profiling results
        save_stats: Whether to save profiling statistics to a file
        print_output: Whether to print profiling results to console
        sort_by: Sorting metric for statistics ("cumulative", "time", "calls", etc.)
        lines_to_print: Number of lines to print in the stats output
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create profiler
            profiler = cProfile.Profile()
            
            try:
                # Start profiling
                start_time = time.perf_counter()
                profiler.enable()
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Stop profiling
                profiler.disable()
                end_time = time.perf_counter()
                
                # Process statistics
                s = io.StringIO()
                stats = pstats.Stats(profiler, stream=s).sort_stats(sort_by)
                
                # Print statistics if requested
                if print_output:
                    stats.print_stats(lines_to_print)
                    logger.info(f"Profile results for {func.__name__}:\n{s.getvalue()}")
                    logger.info(f"Total execution time: {end_time - start_time:.4f} seconds")
                
                # Save statistics to file if requested
                if save_stats and output_dir:
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    stats_file = output_path / f"{func.__name__}_{timestamp}.prof"
                    stats.dump_stats(str(stats_file))
                    logger.info(f"Profiling stats saved to: {stats_file}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error during profiling of {func.__name__}: {str(e)}")
                raise ProfilingError(f"Profiling failed: {str(e)}") from e
            
            finally:
                profiler.disable()
                
        return wrapper
    return decorator
