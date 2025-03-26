import mmh3
from bitarray import bitarray
from redis_client import redis_client
from typing import Union, Optional
import math
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class BloomFilter:
    def __init__(
        self,
        expected_elements: int = 100000,
        false_positive_rate: float = 0.01,
        redis_key: str = "bloom_filter",
        redis_expiry: Optional[int] = None
    ):
        """
        Initialize Bloom Filter with optimal size and hash functions.
        
        Args:
            expected_elements: Expected number of elements to be added
            false_positive_rate: Desired false positive probability
            redis_key: Redis key to store the bloom filter
            redis_expiry: TTL for Redis key in seconds
        """
        self.redis_key = redis_key
        self.redis_expiry = redis_expiry
        
        # Calculate optimal size and hash count
        self.size = self._calculate_optimal_size(expected_elements, false_positive_rate)
        self.hash_count = self._calculate_optimal_hash_count(expected_elements, self.size)
        
        # Initialize bit array
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)
        
        logger.info(f"Initialized BloomFilter: size={self.size}, hash_count={self.hash_count}")

    @staticmethod
    def _calculate_optimal_size(n: int, p: float) -> int:
        """Calculate optimal bit array size."""
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return math.ceil(m)

    @staticmethod
    def _calculate_optimal_hash_count(n: int, m: int) -> int:
        """Calculate optimal number of hash functions."""
        k = (m / n) * math.log(2)
        return math.ceil(k)

    @lru_cache(maxsize=1000)
    def _get_hash_indexes(self, item: str) -> list:
        """Calculate and cache hash indexes for an item."""
        return [mmh3.hash(item, i) % self.size for i in range(self.hash_count)]

    def add(self, item: Union[str, bytes]) -> bool:
        """
        Add an item to the Bloom Filter.
        
        Returns:
            bool: True if addition was successful
        """
        try:
            if isinstance(item, bytes):
                item = item.decode('utf-8')

            indexes = self._get_hash_indexes(item)
            
            # Update local bitarray and Redis
            pipe = redis_client.pipeline()
            for index in indexes:
                self.bit_array[index] = 1
                pipe.setbit(self.redis_key, index, 1)
            
            pipe.execute()
            
            # Set expiry if specified
            if self.redis_expiry:
                redis_client.expire(self.redis_key, self.redis_expiry)
                
            return True
            
        except Exception as e:
            logger.error(f"Error adding item to BloomFilter: {str(e)}")
            return False

    def check(self, item: Union[str, bytes]) -> bool:
        """
        Check if an item might exist in the Bloom Filter.
        
        Returns:
            bool: True if item might exist, False if it definitely doesn't exist
        """
        try:
            if isinstance(item, bytes):
                item = item.decode('utf-8')

            indexes = self._get_hash_indexes(item)
            
            # Check both local bitarray and Redis
            pipe = redis_client.pipeline()
            for index in indexes:
                pipe.getbit(self.redis_key, index)
            
            results = pipe.execute()
            
            return all(results)
            
        except Exception as e:
            logger.error(f"Error checking item in BloomFilter: {str(e)}")
            return False

    def clear(self) -> bool:
        """Clear the Bloom Filter."""
        try:
            self.bit_array.setall(0)
            redis_client.delete(self.redis_key)
            return True
        except Exception as e:
            logger.error(f"Error clearing BloomFilter: {str(e)}")
            return False

    def estimate_elements_count(self) -> int:
        """Estimate the number of elements in the filter."""
        set_bits = sum(1 for bit in self.bit_array if bit)
        return int(-self.size * math.log(1 - set_bits / self.size) / self.hash_count)

# Singleton instance
bloom_filter = BloomFilter()
