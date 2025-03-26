import os
import pytest
from unittest.mock import patch
from typing import Dict, Any
import dotenv
from pathlib import Path

class TestEnvironmentVariables:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        self.original_env = dict(os.environ)
        yield
        os.environ.clear()
        os.environ.update(self.original_env)

    @pytest.fixture
    def mock_env_vars(self) -> Dict[str, str]:
        """Common environment variables for testing"""
        return {
            "JWT_SECRET_KEY": "test_secret_key",
            "API_KEY": "test_api_key",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "REDIS_URL": "redis://localhost:6379",
            "ENVIRONMENT": "test",
            "LOG_LEVEL": "DEBUG",
            "RATE_LIMIT_MAX_REQUESTS": "100",
            "RATE_LIMIT_WINDOW_SECONDS": "60"
        }

    def test_required_env_vars_present(self, mock_env_vars):
        """Test if all required environment variables are present"""
        with patch.dict(os.environ, mock_env_vars):
            required_vars = [
                "JWT_SECRET_KEY",
                "API_KEY",
                "DATABASE_URL",
                "REDIS_URL"
            ]
            missing_vars = [var for var in required_vars if var not in os.environ]
            assert not missing_vars, f"Missing required environment variables: {missing_vars}"

    def test_env_var_types_and_formats(self, mock_env_vars):
        """Test if environment variables have correct types and formats"""
        with patch.dict(os.environ, mock_env_vars):
            # Test numeric values
            assert str.isdigit(os.getenv("RATE_LIMIT_MAX_REQUESTS", "0"))
            assert str.isdigit(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "0"))
            
            # Test URL formats
            assert os.getenv("DATABASE_URL", "").startswith("postgresql://")
            assert os.getenv("REDIS_URL", "").startswith("redis://")

    def test_env_file_loading(self):
        """Test if .env file can be loaded correctly"""
        env_path = Path(".env.test")
        test_env_content = """
        JWT_SECRET_KEY=test_secret_key
        API_KEY=test_api_key
        DATABASE_URL=postgresql://user:pass@localhost:5432/db
        """
        
        try:
            # Create temporary .env.test file
            env_path.write_text(test_env_content)
            
            # Load and verify environment variables
            dotenv.load_dotenv(env_path)
            assert os.getenv("JWT_SECRET_KEY") == "test_secret_key"
            assert os.getenv("API_KEY") == "test_api_key"
        finally:
            # Cleanup
            if env_path.exists():
                env_path.unlink()

    @pytest.mark.parametrize("env_var,expected_type", [
        ("JWT_SECRET_KEY", str),
        ("RATE_LIMIT_MAX_REQUESTS", int),
        ("RATE_LIMIT_WINDOW_SECONDS", int)
    ])
    def test_env_var_type_validation(self, mock_env_vars, env_var: str, expected_type: Any):
        """Test if environment variables can be cast to their expected types"""
        with patch.dict(os.environ, mock_env_vars):
            value = os.getenv(env_var)
            assert value is not None, f"Environment variable {env_var} is not set"
            
            try:
                typed_value = expected_type(value)
                assert isinstance(typed_value, expected_type)
            except ValueError:
                pytest.fail(f"Environment variable {env_var} cannot be cast to {expected_type}")

    def test_environment_specific_vars(self, mock_env_vars):
        """Test environment-specific variable configurations"""
        environments = ["development", "test", "production"]
        
        for env in environments:
            test_vars = mock_env_vars.copy()
            test_vars["ENVIRONMENT"] = env
            
            with patch.dict(os.environ, test_vars):
                assert os.getenv("ENVIRONMENT") == env
                
                # Verify environment-specific configurations
                if env == "production":
                    assert os.getenv("LOG_LEVEL") in ["INFO", "WARNING", "ERROR"]
                elif env == "development":
                    assert os.getenv("LOG_LEVEL") in ["DEBUG", "INFO"]

    @pytest.mark.security
    def test_sensitive_env_vars_masking(self, mock_env_vars):
        """Test if sensitive environment variables are properly masked"""
        sensitive_vars = ["JWT_SECRET_KEY", "API_KEY", "DATABASE_URL"]
        
        with patch.dict(os.environ, mock_env_vars):
            for var in sensitive_vars:
                value = os.getenv(var)
                assert value is not None
                assert len(value) > 0
                # Ensure sensitive values are not logged or exposed
                assert value not in str(os.environ)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
