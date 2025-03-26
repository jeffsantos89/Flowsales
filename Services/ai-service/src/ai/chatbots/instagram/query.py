from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from functools import wraps
import json
from contextlib import asynccontextmanager

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class QueryStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class InstagramQuery:
    """Enhanced data class for Instagram query parameters"""
    user_id: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    priority: QueryPriority = field(default=QueryPriority.MEDIUM)
    status: QueryStatus = field(default=QueryStatus.PENDING)
    retry_count: int = field(default=0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize query to dictionary"""
        return {
            "user_id": self.user_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "priority": self.priority.name,
            "status": self.status.name,
            "retry_count": self.retry_count
        }

def async_retry(max_retries: int = 3, exponential_backoff: bool = True):
    """Decorator for async retry logic"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = 2 ** attempt if exponential_backoff else 1
                        logger.warning(f"Retry attempt {attempt + 1}/{max_retries} after {delay}s delay")
                        await asyncio.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

class QueryProcessor(ABC):
    """Abstract base class for query processing with priority handling"""
    @abstractmethod
    async def process(self, query: InstagramQuery) -> Dict[str, Any]:
        pass
    
    @property
    @abstractmethod
    def processor_name(self) -> str:
        pass

    async def can_process(self, query: InstagramQuery) -> bool:
        """Override to add conditions for processing"""
        return True

@asynccontextmanager
async def query_timeout(timeout: float):
    """Context manager for query timeout"""
    try:
        async with asyncio.timeout(timeout):
            yield
    except asyncio.TimeoutError:
        raise InstagramQueryException("Query processing timeout")

class InstagramQueryHandler:
    """Enhanced handler for Instagram queries with sophisticated features"""
    
    def __init__(self, 
                 max_retries: int = 3, 
                 timeout: float = 30.0,
                 max_cache_size: int = 1000):
        self.max_retries = max_retries
        self.timeout = timeout
        self.max_cache_size = max_cache_size
        self._processors: Dict[str, QueryProcessor] = {}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._processing_lock = asyncio.Lock()
        
    def register_processor(self, processor: QueryProcessor) -> None:
        """Register a new query processor with name check"""
        if not processor.processor_name:
            raise ValueError("Processor must have a name")
        self._processors[processor.processor_name] = processor

    def unregister_processor(self, processor_name: str) -> None:
        """Unregister a query processor"""
        self._processors.pop(processor_name, None)

    @async_retry(max_retries=3)
    async def handle_query(self,
                         user_id: str,
                         message: str,
                         context: Optional[Dict[str, Any]] = None,
                         priority: QueryPriority = QueryPriority.MEDIUM) -> Dict[str, Any]:
        """Enhanced query handling with priority and status tracking"""
        try:
            query = InstagramQuery(
                user_id=user_id,
                message=message,
                context=context or {},
                priority=priority
            )
            
            async with self._processing_lock:
                query.status = QueryStatus.PROCESSING
                response = await self._execute_query(query)
                query.status = QueryStatus.COMPLETED
                
                # Manage cache size
                if len(self._cache) >= self.max_cache_size:
                    self._cleanup_cache()
                
                return response
                
        except Exception as e:
            logger.error(f"Query processing failed for user {user_id}: {str(e)}", exc_info=True)
            query.status = QueryStatus.FAILED
            raise InstagramQueryException(f"Query processing failed: {str(e)}")

    async def _execute_query(self, query: InstagramQuery) -> Dict[str, Any]:
        """Execute query with timeout and processor chain"""
        response = {}
        
        async with query_timeout(self.timeout):
            for processor_name, processor in sorted(
                self._processors.items(),
                key=lambda x: x[1].priority if hasattr(x[1], 'priority') else QueryPriority.MEDIUM
            ):
                if await processor.can_process(query):
                    try:
                        result = await processor.process(query)
                        response.update(result)
                        logger.debug(f"Processor {processor_name} completed successfully")
                    except Exception as e:
                        logger.error(f"Processor {processor_name} failed: {str(e)}", exc_info=True)
                        
        if not response:
            raise InstagramQueryException("No successful query processing")
            
        self._cache[query.user_id] = response
        return response

    def _cleanup_cache(self) -> None:
        """Remove oldest entries when cache is full"""
        sorted_cache = sorted(self._cache.items(), key=lambda x: x[1].get('timestamp', datetime.min))
        items_to_remove = len(self._cache) - self.max_cache_size + 1
        for i in range(items_to_remove):
            self._cache.pop(sorted_cache[i][0], None)

    def clear_cache(self, user_id: Optional[str] = None) -> None:
        """Clear cache with optional user filter"""
        if user_id:
            self._cache.pop(user_id, None)
        else:
            self._cache.clear()

class InstagramQueryException(Exception):
    """Custom exception with enhanced error details"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}
