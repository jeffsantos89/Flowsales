import os
import pytest
from typing import Dict, Any
from unittest.mock import patch
from dataclasses import dataclass

@dataclass
class ExpectedEnvConfig:
    """Data class to hold expected environment configuration"""
    key: str
    value: Any
    required: bool = True
    default: Any = None

class EnvVarTestError(Exception):
    """Custom exception for environment variable testing errors"""
    pass

@pytest.fixture(scope="module")
def required_env_vars() -> Dict[str, ExpectedEnvConfig]:
    """Fixture that defines expected environment variables and their configurations"""
    return {
        "DATABASE_URL": ExpectedEnvConfig(
            key="DATABASE_URL",
            value="postgresql://user:pass@localhost:5432/db",
            required=True
        ),
        "API_KEY": ExpectedEnvConfig(
            key="API_KEY",
            value="test-api-key-123",
            required=True
        ),
        "DEBUG": ExpectedEnvConfig(
            key="DEBUG",
            value="False",
            required=False,
            default="False"
        ),
        "MAX_CONNECTIONS": ExpectedEnvConfig(
            key="MAX_CONNECTIONS",
            value="100",
            required=False,
            default="50"
        )
    }

@pytest.fixture(autouse=True)
def setup_env_vars(required_env_vars):
    """Setup and teardown for environment variables"""
    original_environ = dict(os.environ)
    
    # Setup environment variables for testing
    for config in required_env_vars.values():
        os.environ[config.key] = config.value
    
    yield
    
    # Restore original environment after tests
    os.environ.clear()
    os.environ.update(original_environ)

def test_required_env_vars_present(required_env_vars):
    """Test that all required environment variables are present"""
    for config in required_env_vars.values():
        if config.required:
            assert os.getenv(config.key) is not None, f"Required environment variable {config.key} is missing"
            assert os.getenv(config.key) == config.value, f"Environment variable {config.key} has unexpected value"

def test_env_var_types(required_env_vars):
    """Test environment variable type conversions"""
    # Test boolean conversion
    assert str(os.getenv("DEBUG")).lower() in ("true", "false")
    
    # Test integer conversion
    max_connections = os.getenv("MAX_CONNECTIONS")
    assert max_connections.isdigit(), "MAX_CONNECTIONS must be a number"
    assert 0 <= int(max_connections) <= 1000, "MAX_CONNECTIONS must be between 0 and 1000"

@pytest.mark.parametrize("env_key,invalid_value", [
    ("DATABASE_URL", "invalid-url"),
    ("API_KEY", ""),
    ("MAX_CONNECTIONS", "not_a_number"),
])
def test_invalid_env_vars(env_key: str, invalid_value: str):
    """Test handling of invalid environment variable values"""
    with patch.dict(os.environ, {env_key: invalid_value}):
        if env_key == "DATABASE_URL":
            assert "postgresql://" in os.getenv("DATABASE_URL", ""), "Invalid database URL format"
        elif env_key == "API_KEY":
            assert os.getenv("API_KEY", ""), "API_KEY cannot be empty"
        elif env_key == "MAX_CONNECTIONS":
            with pytest.raises(ValueError):
                int(os.getenv("MAX_CONNECTIONS", ""))

def test_default_values(required_env_vars):
    """Test default values for optional environment variables"""
    for config in required_env_vars.values():
        if not config.required:
            # Temporarily remove the environment variable
            with patch.dict(os.environ):
                os.environ.pop(config.key, None)
                assert os.getenv(config.key, config.default) == config.default

def test_sensitive_data_masking():
    """Test that sensitive environment variables are properly masked"""
    sensitive_vars = ["API_KEY", "DATABASE_URL"]
    
    def mask_sensitive_value(value: str) -> str:
        return f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****"
    
    for var in sensitive_vars:
        value = os.getenv(var)
        if value:
            masked_value = mask_sensitive_value(value)
            assert len(masked_value.strip(".*")) <= 8, f"Sensitive data in {var} might be exposed"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])