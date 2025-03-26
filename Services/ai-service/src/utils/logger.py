import os
import unittest
from unittest.mock import patch
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager

class EnvironmentVariableTestCase(unittest.TestCase):
    """Test suite for environment variables validation and management."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test environment before all tests."""
        cls.required_vars = {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db',
            'API_KEY': 'test-api-key-123',
            'ENVIRONMENT': 'test',
            'LOG_LEVEL': 'DEBUG'
        }
        cls.optional_vars = {
            'CACHE_TTL': '3600',
            'MAX_RETRIES': '3',
            'TIMEOUT': '30'
        }

    def setUp(self) -> None:
        """Set up test environment before each test."""
        self.env_backup = dict(os.environ)
        self.cleanup_env()

    def tearDown(self) -> None:
        """Clean up test environment after each test."""
        os.environ.clear()
        os.environ.update(self.env_backup)

    @staticmethod
    def cleanup_env() -> None:
        """Remove test-specific environment variables."""
        for key in list(os.environ.keys()):
            if key.startswith('TEST_'):
                del os.environ[key]

    @contextmanager
    def env_vars(self, **kwargs: Dict[str, str]) -> None:
        """Context manager for temporary environment variables."""
        original = {k: os.environ.get(k) for k in kwargs}
        os.environ.update({k: str(v) for k, v in kwargs.items()})
        try:
            yield
        finally:
            for k, v in original.items():
                if v is None:
                    del os.environ[k]
                else:
                    os.environ[k] = v

    def test_required_environment_variables(self) -> None:
        """Test that all required environment variables are present."""
        with self.env_vars(**self.required_vars):
            for var_name, expected_value in self.required_vars.items():
                self.assertEqual(os.environ.get(var_name), expected_value)
                self.assertIsNotNone(os.environ.get(var_name))

    def test_missing_required_variables(self) -> None:
        """Test handling of missing required environment variables."""
        for var_name in self.required_vars:
            with self.assertRaises(KeyError):
                self._get_required_env_var(var_name)

    def test_optional_environment_variables(self) -> None:
        """Test optional environment variables with default values."""
        with self.env_vars(**self.optional_vars):
            for var_name, expected_value in self.optional_vars.items():
                self.assertEqual(os.environ.get(var_name), expected_value)

    def test_environment_type_casting(self) -> None:
        """Test type casting of environment variables."""
        test_vars = {
            'TEST_INT': '42',
            'TEST_FLOAT': '3.14',
            'TEST_BOOL': 'true',
            'TEST_LIST': '1,2,3,4,5'
        }
        
        with self.env_vars(**test_vars):
            self.assertEqual(self._cast_env_var('TEST_INT', int), 42)
            self.assertEqual(self._cast_env_var('TEST_FLOAT', float), 3.14)
            self.assertEqual(self._cast_env_var('TEST_BOOL', self._to_bool), True)
            self.assertEqual(
                self._cast_env_var('TEST_LIST', lambda x: [int(i) for i in x.split(',')]),
                [1, 2, 3, 4, 5]
            )

    @staticmethod
    def _get_required_env_var(var_name: str) -> str:
        """Get required environment variable or raise error."""
        value = os.environ.get(var_name)
        if value is None:
            raise KeyError(f"Required environment variable '{var_name}' is not set")
        return value

    @staticmethod
    def _cast_env_var(var_name: str, cast_func: callable) -> Any:
        """Cast environment variable to specified type."""
        value = os.environ.get(var_name)
        try:
            return cast_func(value) if value is not None else None
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to cast {var_name} to {cast_func.__name__}: {e}")

    @staticmethod
    def _to_bool(value: str) -> bool:
        """Convert string to boolean."""
        return str(value).lower() in ('true', '1', 'yes', 'on')

    def test_environment_validation(self) -> None:
        """Test environment validation logic."""
        valid_environments = {'development', 'staging', 'production', 'test'}
        
        with self.env_vars(ENVIRONMENT='invalid'):
            with self.assertRaises(ValueError):
                self._validate_environment(valid_environments)

        with self.env_vars(ENVIRONMENT='production'):
            self.assertTrue(self._validate_environment(valid_environments))

    @staticmethod
    def _validate_environment(valid_environments: set) -> bool:
        """Validate current environment."""
        current_env = os.environ.get('ENVIRONMENT', '').lower()
        if current_env not in valid_environments:
            raise ValueError(f"Invalid environment: {current_env}")
        return True