import pytest
import time
import logging
import statistics
from typing import List, Dict
from contextlib import contextmanager
from datetime import datetime
from pymongo import MongoClient
from sqlalchemy import create_engine
from redis import Redis
import psutil
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='db_performance_tests.log'
)
logger = logging.getLogger(__name__)

class DatabasePerformanceTest:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.postgres_engine = create_engine('postgresql://user:password@localhost:5432/testdb')
        self.redis_client = Redis(host='localhost', port=6379, decode_responses=True)

    @contextmanager
    def measure_performance(self, operation_name: str):
        """Context manager to measure operation performance"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            memory_used = end_memory - start_memory
            
            if operation_name not in self.metrics:
                self.metrics[operation_name] = []
            
            self.metrics[operation_name].append({
                'duration_ms': duration,
                'memory_mb': memory_used,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"{operation_name}: Duration={duration:.2f}ms, Memory={memory_used:.2f}MB")

    def generate_test_data(self, size: int) -> List[Dict]:
        """Generate test data for database operations"""
        return [
            {
                'id': i,
                'name': f'Test{i}',
                'data': 'x' * 1000,  # 1KB of data
                'timestamp': datetime.now().isoformat()
            }
            for i in range(size)
        ]

    def analyze_results(self, operation_name: str) -> Dict:
        """Analyze performance metrics for an operation"""
        if operation_name not in self.metrics:
            return {}

        durations = [m['duration_ms'] for m in self.metrics[operation_name]]
        memory_usage = [m['memory_mb'] for m in self.metrics[operation_name]]

        return {
            'operation': operation_name,
            'samples': len(durations),
            'duration': {
                'mean': statistics.mean(durations),
                'median': statistics.median(durations),
                'std_dev': statistics.stdev(durations) if len(durations) > 1 else 0,
                'min': min(durations),
                'max': max(durations)
            },
            'memory': {
                'mean': statistics.mean(memory_usage),
                'median': statistics.median(memory_usage),
                'std_dev': statistics.stdev(memory_usage) if len(memory_usage) > 1 else 0,
                'min': min(memory_usage),
                'max': max(memory_usage)
            }
        }

    def export_results(self, filename: str):
        """Export test results to JSON file"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total / (1024 * 1024 * 1024)  # GB
            },
            'metrics': {
                op: self.analyze_results(op)
                for op in self.metrics.keys()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

@pytest.fixture
def db_performance():
    return DatabasePerformanceTest()

def test_mongodb_performance(db_performance):
    """Test MongoDB performance"""
    test_data = db_performance.generate_test_data(1000)
    db = db_performance.mongo_client['test_db']
    collection = db['test_collection']

    # Test bulk insert
    with db_performance.measure_performance('mongodb_bulk_insert'):
        collection.insert_many(test_data)

    # Test bulk read
    with db_performance.measure_performance('mongodb_bulk_read'):
        list(collection.find({}))

    # Test indexed query
    with db_performance.measure_performance('mongodb_indexed_query'):
        collection.create_index('id')
        list(collection.find({'id': {'$lt': 500}}))

def test_postgres_performance(db_performance):
    """Test PostgreSQL performance"""
    test_data = db_performance.generate_test_data(1000)
    
    # Test bulk insert
    with db_performance.measure_performance('postgres_bulk_insert'):
        with db_performance.postgres_engine.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    data TEXT,
                    timestamp TIMESTAMP
                )
            """)
            conn.execute("INSERT INTO test_table VALUES (:id, :name, :data, :timestamp)", test_data)

    # Test bulk read
    with db_performance.measure_performance('postgres_bulk_read'):
        with db_performance.postgres_engine.connect() as conn:
            conn.execute("SELECT * FROM test_table").fetchall()

def test_redis_performance(db_performance):
    """Test Redis performance"""
    test_data = db_performance.generate_test_data(1000)
    
    # Test bulk insert
    with db_performance.measure_performance('redis_bulk_insert'):
        pipeline = db_performance.redis_client.pipeline()
        for item in test_data:
            pipeline.hset(f"test:{item['id']}", mapping=item)
        pipeline.execute()

    # Test bulk read
    with db_performance.measure_performance('redis_bulk_read'):
        pipeline = db_performance.redis_client.pipeline()
        for i in range(1000):
            pipeline.hgetall(f"test:{i}")
        pipeline.execute()

if __name__ == '__main__':
    # Run tests and export results
    performance_test = DatabasePerformanceTest()
    pytest.main([__file__])
    performance_test.export_results('performance_results.json')