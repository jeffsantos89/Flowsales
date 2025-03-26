import cProfile
import pstats
import io
import functools
import logging
from typing import Callable, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ProfilingError(Exception):
    """Custom exception for profiling errors."""
    pass

def profile_function(
    output_dir: Optional[str] = None,
    stats_count: int = 20,
    sort_by: str = "cumulative",
    save_to_file: bool = False
) -> Callable:
    """
    Advanced profiling decorator with configurable options.
    
    Args:
        output_dir: Directory to save profiling results
        stats_count: Number of stats to display/save
        sort_by: Sorting criteria for stats ('cumulative', 'time', 'calls', etc.)
        save_to_file: Whether to save results to a file
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Initialize profiler
                profiler = cProfile.Profile()
                profiler.enable()

                # Execute function
                result = func(*args, **kwargs)

                # Stop profiling
                profiler.disable()

                # Process stats
                s = io.StringIO()
                stats = pstats.Stats(profiler, stream=s).sort_stats(sort_by)
                
                # Print limited number of stats
                stats.print_stats(stats_count)
                profile_output = s.getvalue()

                # Log the results
                logger.info(f"Profile results for {func.__name__}:\n{profile_output}")

                # Save to file if requested
                if save_to_file and output_dir:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    filename = output_path / f"profile_{func.__name__}_{timestamp}.txt"
                    with open(filename, 'w') as f:
                        f.write(profile_output)
                    logger.info(f"Profile results saved to {filename}")

                return result

            except Exception as e:
                logger.error(f"Profiling failed for {func.__name__}: {str(e)}")
                raise ProfilingError(f"Profiling failed: {str(e)}") from e

        return wrapper
    return decorator
