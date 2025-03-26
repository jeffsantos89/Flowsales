import logging
import os
from .file_utils import read_file, write_file
from .data_processing import process_data, clean_data
from .math_utils import calculate_mean, calculate_median

# __init__.py

"""
Utils Package

This package contains utility modules and functions that are used across the ai-service project.
"""


# Configure logging for the utils package
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import utility modules

# Ensure necessary environment variables are set
REQUIRED_ENV_VARS = ['ENV_VAR_1', 'ENV_VAR_2']

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        logger.warning(f"Environment variable {var} is not set.")

logger.info("Utils package initialized successfully.")