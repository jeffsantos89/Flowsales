import os
from dotenv import load_dotenv
import logging
from typing import Any, Dict, Optional
from functools import lru_cache

class EnvLoader:
    @staticmethod
    def load_env():
        load_dotenv()

    @staticmethod
    def get_env_var(var_name: str, default_value=None):
        return os.getenv(var_name, default_value)

env_loader = EnvLoader()
class EnvLoaderError(Exception):
    """Custom exception for environment loading errors"""
    pass

class EnvLoader:
    _instance = None
    _env_cache: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._setup_logging()
        return cls._instance

    @staticmethod
    def _setup_logging():
        logging.basicConfig(level=logging.INFO)
        
    @classmethod
    def load_env(cls, env_file: str = '.env') -> None:
        try:
            if not os.path.exists(env_file):
                raise EnvLoaderError(f"Environment file {env_file} not found")
            load_dotenv(env_file)
            logging.info(f"Environment loaded successfully from {env_file}")
        except Exception as e:
            logging.error(f"Failed to load environment: {str(e)}")
            raise EnvLoaderError(f"Environment loading failed: {str(e)}")

    @classmethod
    @lru_cache(maxsize=128)
    def get_env_var(cls, var_name: str, default_value: Optional[Any] = None, required: bool = False) -> Any:
        if var_name in cls._env_cache:
            return cls._env_cache[var_name]

        value = os.getenv(var_name, default_value)
        
        if required and value is None:
            raise EnvLoaderError(f"Required environment variable {var_name} is not set")
            
        cls._env_cache[var_name] = value
        return value

    @classmethod
    def clear_cache(cls) -> None:
        cls._env_cache.clear()
        cls.get_env_var.cache_clear()

env_loader = EnvLoader()