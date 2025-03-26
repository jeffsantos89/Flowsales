import os
import pytest
from typing import Generator, Any
import tempfile
from pathlib import Path
from unittest.mock import patch
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class EnvironmentVariableError(Exception):
    """Custom exception for environment variable related errors"""
    pass

@contextmanager
def temp_env_vars(**kwargs: Any) -> Generator[None, None, None]:
    """Context manager for temporarily setting environment variables"""
    original_env = {}
    try:
        for key, value in kwargs.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = str(value)
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

class TestEnvironmentVariables:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self) -> Generator[None, None, None]:
        """Setup and teardown for each test"""
        # Setup
        self.required_vars = [
            'DATABASE_URL',
            'API_KEY',
            'ENVIRONMENT',
            'LOG_LEVEL'
        ]
        self.test_env_values = {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db',
            'API_KEY': 'test_key_123',
            'ENVIRONMENT': 'test',
            'LOG_LEVEL': 'DEBUG'
        }
        
        yield
        
        # Teardown
        for var in self.required_vars:
            if var in os.environ:
                del os.environ[var]

    def test_env_vars_present(self) -> None:
        """Test if all required environment variables are present"""
        with temp_env_vars(**self.test_env_values):
            for var in self.required_vars:
                assert os.getenv(var) is not None, f"Environment variable {var} is missing"
                assert os.getenv(var) == self.test_env_values[var]

    def test_env_vars_missing(self) -> None:
        """Test handling of missing environment variables"""
        for var in self.required_vars:
            if var in os.environ:
                del os.environ[var]
        
        with pytest.raises(EnvironmentVariableError) as exc_info:
            self._validate_required_vars()
        
        assert "Missing required environment variables" in str(exc_info.value)

    def test_env_vars_types(self) -> None:
        """Test environment variable type validation"""
        test_cases = {
            'PORT': '8080',
            'MAX_CONNECTIONS': '100',
            'DEBUG_MODE': 'true',
            'TIMEOUT': '30.5'
        }

        with temp_env_vars(**test_cases):
            assert self._validate_int('PORT') == 8080
            assert self._validate_int('MAX_CONNECTIONS') == 100
            assert self._validate_bool('DEBUG_MODE') is True
            assert self._validate_float('TIMEOUT') == 30.5

    def test_env_vars_from_file(self) -> None:
        """Test loading environment variables from file"""
        env_content = '\n'.join([f'{k}={v}' for k, v in self.test_env_values.items()])
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(env_content)
            temp_file.flush()
            
            loaded_vars = self._load_env_file(temp_file.name)
            
            assert loaded_vars == self.test_env_values
            
        Path(temp_file.name).unlink()

    @pytest.mark.parametrize("env_name,expected_config", [
        ('development', {'debug': True, 'log_level': 'DEBUG'}),
        ('production', {'debug': False, 'log_level': 'INFO'}),
        ('staging', {'debug': True, 'log_level': 'INFO'})
    ])
    def test_environment_specific_config(self, env_name: str, expected_config: dict) -> None:
        """Test environment-specific configuration loading"""
        with temp_env_vars(ENVIRONMENT=env_name):
            config = self._get_environment_config()
            assert config == expected_config

    @staticmethod
    def _validate_required_vars() -> None:
        """Validate presence of required environment variables"""
        missing_vars = [var for var in ['DATABASE_URL', 'API_KEY', 'ENVIRONMENT']
                       if not os.getenv(var)]
        
        if missing_vars:
            raise EnvironmentVariableError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    @staticmethod
    def _validate_int(var_name: str) -> int:
        """Validate and convert environment variable to integer"""
        try:
            return int(os.getenv(var_name, '0'))
        except ValueError:
            raise EnvironmentVariableError(f"Environment variable {var_name} must be an integer")

    @staticmethod
    def _validate_bool(var_name: str) -> bool:
        """Validate and convert environment variable to boolean"""
        return os.getenv(var_name, '').lower() == 'true'

    @staticmethod
    def _validate_float(var_name: str) -> float:
        """Validate and convert environment variable to float"""
        try:
            return float(os.getenv(var_name, '0.0'))
        except ValueError:
            raise EnvironmentVariableError(f"Environment variable {var_name} must be a float")

    @staticmethod
    def _load_env_file(file_path: str) -> dict:
        """Load environment variables from file"""
        env_vars = {}
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error loading environment file: {e}")
            raise EnvironmentVariableError(f"Failed to load environment file: {e}")
        
        return env_vars

    @staticmethod
    def _get_environment_config() -> dict:
        """Get environment-specific configuration"""
        env = os.getenv('ENVIRONMENT', 'development')
        configs = {
            'development': {'debug': True, 'log_level': 'DEBUG'},
            'staging': {'debug': True, 'log_level': 'INFO'},
            'production': {'debug': False, 'log_level': 'INFO'}
        }
        return configs.get(env, configs['development'])
