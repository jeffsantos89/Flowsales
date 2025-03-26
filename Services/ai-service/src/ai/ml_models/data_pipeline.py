from pathlib import Path
import pandas as pd
import logging
from typing import Union, Optional, Dict, Any
from datetime import datetime
import numpy as np
from pandas.errors import EmptyDataError
from dataclasses import dataclass
from abc import ABC, abstractmethod
import yaml
import joblib
from concurrent.futures import ThreadPoolExecutor
import os

@dataclass
class DataConfig:
    """Configuration settings for data processing"""
    raw_data_path: Path
    output_path: Path
    allowed_extensions: tuple = ('.csv', '.parquet', '.xlsx')
    chunk_size: int = 10000
    n_workers: int = os.cpu_count() or 1

class DataValidator:
    """Validates data quality and integrity"""
    
    @staticmethod
    def validate_schema(df: pd.DataFrame, schema: Dict[str, Any]) -> bool:
        """Validates DataFrame schema against expected schema"""
        try:
            for column, dtype in schema.items():
                if column not in df.columns:
                    raise ValueError(f"Missing column: {column}")
                if not np.issubdtype(df[column].dtype, dtype):
                    raise TypeError(f"Invalid dtype for {column}: expected {dtype}, got {df[column].dtype}")
            return True
        except Exception as e:
            raise ValueError(f"Schema validation failed: {str(e)}")

class DataPipeline:
    """Enhanced data pipeline for transformation and preparation."""

    def __init__(
        self, 
        config_path: Union[str, Path],
        env: str = "production"
    ):
        self.config = self._load_config(config_path, env)
        self.data_config = DataConfig(**self.config['data'])
        self._setup_logging()
        self.validator = DataValidator()
        self.processed_data = None

    def _load_config(self, config_path: Union[str, Path], env: str) -> Dict[str, Any]:
        """Loads configuration from YAML file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config[env]

    def _setup_logging(self) -> None:
        """Sets up logging with enhanced configuration"""
        self.logger = logging.getLogger(__name__)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # Add file handler for persistent logging
            file_handler = logging.FileHandler(
                self.data_config.output_path / 'pipeline.log'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            self.logger.setLevel(logging.INFO)

    def validate_input_path(self) -> None:
        """Validates input file existence and format"""
        if not self.data_config.raw_data_path.exists():
            raise FileNotFoundError(
                f"File not found: {self.data_config.raw_data_path}"
            )
        if self.data_config.raw_data_path.suffix not in self.data_config.allowed_extensions:
            raise ValueError(
                f"Invalid file format. Allowed: {self.data_config.allowed_extensions}"
            )

    def load_data(self) -> pd.DataFrame:
        """Loads data with enhanced error handling and chunking support"""
        self.validate_input_path()
        
        try:
            self.logger.info(f"Loading data from {self.data_config.raw_data_path}")
            
            if self.data_config.raw_data_path.suffix == '.csv':
                chunks = pd.read_csv(
                    self.data_config.raw_data_path,
                    chunksize=self.data_config.chunk_size
                )
                with ThreadPoolExecutor(max_workers=self.data_config.n_workers) as executor:
                    dfs = list(executor.map(lambda x: x, chunks))
                df = pd.concat(dfs, ignore_index=True)
            
            elif self.data_config.raw_data_path.suffix == '.parquet':
                df = pd.read_parquet(self.data_config.raw_data_path)
            
            else:  # .xlsx
                df = pd.read_excel(self.data_config.raw_data_path)

            if df.empty:
                raise EmptyDataError("The file is empty")

            self.logger.info(f"Data loaded successfully: {len(df)} records")
            self.processed_data = df
            return df

        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def transform_data(
        self,
        df: Optional[pd.DataFrame] = None,
        min_price: float = 0.0
    ) -> pd.DataFrame:
        """Transforms data with validation and error handling"""
        df = df if df is not None else self.processed_data
        if df is None:
            raise ValueError("No data available for transformation")
