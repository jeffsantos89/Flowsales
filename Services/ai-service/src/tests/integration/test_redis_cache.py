import pytest
import redis
import json
from datetime import timedelta
from typing import Any
from unittest.mock import Mock, patch
import time
import zlib

class TestRedisCache:
    @pytest.fixture(scope="class")
    def redis_client(self):
        """Setup Redis client for testing"""
        client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        # Clear test database before running tests
        client.flushdb()
        yield client
        # Cleanup after tests
        client.flushdb()
        client.close()

    @pytest.fixture
    def cache_key(self) -> str:
        return "test:key"

    @pytest.fixture
    def sample_data(self) -> dict:
        return {
            "id": 1,
            "name": "Test Item",
            "attributes": ["attr1", "attr2"],
            "metadata": {"category": "test"}
        }

    def test_set_and_get_data(self, redis_client, cache_key, sample_data):
        """Test basic set and get operations"""
        # Set data
        redis_client.set(
            cache_key,
            json.dumps(sample_data),
            ex=timedelta(minutes=5)
        )

        # Get data
        cached_data = json.loads(redis_client.get(cache_key))
        assert cached_data == sample_data

    def test_cache_expiration(self, redis_client, cache_key, sample_data):
        """Test cache expiration functionality"""
        # Set with 1 second expiration
        redis_client.set(
            cache_key,
            json.dumps(sample_data),
            ex=1
        )

        # Verify data exists
        assert redis_client.get(cache_key) is not None

        # Wait for expiration
        time.sleep(1.1)

        # Verify data expired
        assert redis_client.get(cache_key) is None

    def test_delete_cache(self, redis_client, cache_key, sample_data):
        """Test cache deletion"""
        redis_client.set(cache_key, json.dumps(sample_data))
        assert redis_client.delete(cache_key) == 1
        assert redis_client.get(cache_key) is None

    @pytest.mark.parametrize("test_data", [
        {"simple": "data"},
        {"nested": {"data": "value"}},
        ["list", "of", "items"],
        123,
        "string",
        None
    ])
    def test_various_data_types(self, redis_client, cache_key, test_data):
        """Test handling of various data types"""
        redis_client.set(
            cache_key,
            json.dumps(test_data),
            ex=timedelta(minutes=5)
        )
        assert json.loads(redis_client.get(cache_key)) == test_data

    @patch('redis.Redis')
    def test_connection_error_handling(self, mock_redis):
        """Test Redis connection error handling"""
        mock_redis.side_effect = redis.ConnectionError
        
        with pytest.raises(redis.ConnectionError):
            redis.Redis(
                host='nonexistent',
                port=6379,
                socket_timeout=1
            )

    def test_batch_operations(self, redis_client):
        """Test batch operations using pipeline"""
        test_data = {f"key:{i}": f"value:{i}" for i in range(5)}
        
        with redis_client.pipeline() as pipe:
            for key, value in test_data.items():
                pipe.set(key, value)
            pipe.execute()

        # Verify all data was set correctly
        for key, value in test_data.items():
            assert redis_client.get(key) == value

    @pytest.mark.parametrize("compression_level", [1, 5, 9])
    def test_large_data_handling(self, redis_client, compression_level):
        """Test handling of large data with compression"""
        
        # Generate large data
        large_data = {f"key_{i}": "x" * 1000 for i in range(100)}
        
        # Compress data
        compressed_data = zlib.compress(
            json.dumps(large_data).encode(),
            compression_level
        )
        
        key = f"large_data:{compression_level}"
        redis_client.set(key, compressed_data)
        
        # Retrieve and decompress
        retrieved_data = json.loads(
            zlib.decompress(redis_client.get(key)).decode()
        )
        
        assert retrieved_data == large_data
