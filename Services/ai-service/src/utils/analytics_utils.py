import logging
from typing import Dict, Any
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsUtils:
    @staticmethod
    def calculate_statistics(data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate basic statistics for a given DataFrame.

        :param data: Input DataFrame
        :return: Dictionary with statistics
        """
        logger.info("Calculating statistics for the DataFrame")
        try:
            stats = {
                'mean': data.mean().to_dict(),
                'median': data.median().to_dict(),
                'std_dev': data.std().to_dict(),
                'variance': data.var().to_dict(),
                'min': data.min().to_dict(),
                'max': data.max().to_dict(),
                'count': data.count().to_dict()
            }
            logger.info("Statistics calculation successful")
            return stats
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            raise

    @staticmethod
    def detect_outliers(data: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect outliers in the DataFrame using Z-score method.

        :param data: Input DataFrame
        :param threshold: Z-score threshold to identify outliers
        :return: DataFrame with outliers marked
        """
        logger.info("Detecting outliers in the DataFrame")
        try:
            z_scores = np.abs((data - data.mean()) / data.std())
            outliers = z_scores > threshold
            logger.info("Outlier detection successful")
            return outliers
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            raise

    @staticmethod
    def normalize_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the DataFrame using Min-Max scaling.

        :param data: Input DataFrame
        :return: Normalized DataFrame
        """
        logger.info("Normalizing the DataFrame")
        try:
            normalized_data = (data - data.min()) / (data.max() - data.min())
            logger.info("Data normalization successful")
            return normalized_data
        except Exception as e:
            logger.error(f"Error normalizing data: {e}")
            raise

    @staticmethod
    def fill_missing_values(data: pd.DataFrame, method: str = 'mean') -> pd.DataFrame:
        """
        Fill missing values in the DataFrame.

        :param data: Input DataFrame
        :param method: Method to fill missing values ('mean', 'median', 'mode')
        :return: DataFrame with filled missing values
        """
        logger.info(f"Filling missing values using {method} method")
        try:
            if method == 'mean':
                filled_data = data.fillna(data.mean())
            elif method == 'median':
                filled_data = data.fillna(data.median())
            elif method == 'mode':
                filled_data = data.fillna(data.mode().iloc[0])
            else:
                raise ValueError("Invalid method. Use 'mean', 'median', or 'mode'.")
            logger.info("Missing values filled successfully")
            return filled_data
        except Exception as e:
            logger.error(f"Error filling missing values: {e}")
            raise