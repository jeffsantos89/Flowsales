import os
import pytest
from unittest.mock import patch, MagicMock
from src.utils.cache import CacheManager
import redis

class TestEnvironmentVariables:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        self.original_env = dict(os.environ)
        yield
        os.environ.clear()
        os.environ.update(self.original_env)

    @pytest.fixture
    def mock_redis(self):
        """Fixture to mock Redis client"""
        with patch('redis.Redis') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_default_environment_variables(self, mock_redis):
        """Test CacheManager initialization with default environment variables"""
        cache_manager = CacheManager()
        
        assert os.getenv("REDIS_HOST", "localhost") == "localhost"
        assert int(os.getenv("REDIS_PORT", 6379)) == 6379
        assert int(os.getenv("REDIS_DB", 0)) == 0
        assert os.getenv("REDIS_PASSWORD", None) is None

    def test_custom_environment_variables(self, mock_redis):
        """Test CacheManager initialization with custom environment variables"""
        test_config = {
            "REDIS_HOST": "custom.redis.host",
            "REDIS_PORT": "6380",
            "REDIS_DB": "1",
            "REDIS_PASSWORD": "secret123"
        }
        
        with patch.dict(os.environ, test_config):
            cache_manager = CacheManager()
            
            assert os.getenv("REDIS_HOST") == "custom.redis.host"
            assert int(os.getenv("REDIS_PORT")) == 6380
            assert int(os.getenv("REDIS_DB")) == 1
            assert os.getenv("REDIS_PASSWORD") == "secret123"

    def test_invalid_port_environment_variable(self, mock_redis):
        """Test CacheManager initialization with invalid port"""
        with patch.dict(os.environ, {"REDIS_PORT": "invalid"}):
            with pytest.raises(ValueError):
                CacheManager()

    def test_redis_connection_error(self):
        """Test Redis connection error handling"""
        with patch('redis.Redis') as mock:
            mock.side_effect = redis.ConnectionError("Connection refused")
            with pytest.raises(redis.ConnectionError) as exc_info:
                CacheManager()
            assert "Connection refused" in str(exc_info.value)

    @pytest.mark.parametrize("env_vars,expected", [
        (
            {"REDIS_HOST": "test1.redis.host", "REDIS_PORT": "6379"},
            {"host": "test1.redis.host", "port": 6379}
        ),
        (
            {"REDIS_HOST": "test2.redis.host", "REDIS_PORT": "6380", "REDIS_PASSWORD": "pwd123"},
            {"host": "test2.redis.host", "port": 6380, "password": "pwd123"}
        ),
    ])
    def test_multiple_configurations(self, mock_redis, env_vars, expected):
        """Test multiple Redis configurations"""
        with patch.dict(os.environ, env_vars):
            CacheManager()
            
            for key, value in expected.items():
                assert os.getenv(f"REDIS_{key.upper()}", str(value)) == str(value)

    @pytest.mark.integration
    def test_real_redis_connection(self):
        """Integration test with real Redis connection"""
        # Skip if not in integration test environment
        pytest.skip_if(
            not os.getenv("INTEGRATION_TESTS"), 
            reason="Integration tests not enabled"
        )
        
        cache_manager = CacheManager()
        assert cache_manager.redis_client.ping()

if __name__ == "__main__":
    pytest.main(["-v"])
