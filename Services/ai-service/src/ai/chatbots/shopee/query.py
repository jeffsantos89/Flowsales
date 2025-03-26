from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime
import aiohttp
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import uuid
from enum import Enum

# Advanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('shopee_query.log')
    ]
)
logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    PRODUCT_SEARCH = "product_search"
    PRICE_COMPARISON = "price_comparison"
    SHIPPING_INFO = "shipping_info"
    RETURN_POLICY = "return_policy"
    UNKNOWN = "unknown"
    ERROR = "error"

@dataclass
class QueryContext:
    user_id: str
    session_id: str
    timestamp: datetime
    language: str = "pt-BR"
    platform: str = "shopee"

@dataclass
class ShopeeQueryConfig:
    """Configuration class for Shopee queries"""
    base_url: str
    api_key: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    max_query_length: int = 1000
    rate_limit: int = 100  # requests per minute
    cache_ttl: int = 300  # seconds

class QueryException(Exception):
    """Custom exception for query-related errors"""
    def __init__(self, message: str, error_code: str = None, status_code: int = None):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code

class BaseShopeeQuery(ABC):
    """Abstract base class for Shopee queries"""
    
    def __init__(self, config: ShopeeQueryConfig, nlp_processor: Any):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.nlp_processor = nlp_processor
        self._rate_limiter = asyncio.Semaphore(self.config.rate_limit)
        self._cache = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "ShopeeAPI/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _generate_cache_key(self, params: Dict) -> str:
        return json.dumps(params, sort_keys=True)

    async def _handle_rate_limiting(self):
        async with self._rate_limiter:
            await asyncio.sleep(1)  # Ensure we don't exceed rate limit
    
    @abstractmethod
    async def execute_query(self, *args, **kwargs):
        pass

class ShopeeQueryPipeline:
    """NLP pipeline for processing Shopee queries"""
    
    def __init__(self, nlp_processor: Any):
        self.nlp_processor = nlp_processor

    async def process(self, text: str, context: QueryContext) -> Dict[str, Any]:
        try:
            cleaned_text = self._clean_text(text)
            nlp_result = await self.nlp_processor.analyze(cleaned_text)
            
            return {
                "query_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "intent": nlp_result.get("intent", QueryIntent.UNKNOWN.value),
                "entities": nlp_result.get("entities", []),
                "context": {
                    "user_id": context.user_id,
                    "session_id": context.session_id,
                    "language": context.language
                }
            }
        except Exception as e:
            logger.exception("Error in NLP pipeline")
            return {
                "intent": QueryIntent.ERROR.value,
                "error": str(e)
            }

    def _clean_text(self, text: str) -> str:
        return " ".join(text.strip().lower().split())

class ShopeeProductQuery(BaseShopeeQuery):
    """Class for handling Shopee product-specific queries"""
    
    async def execute_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        await self._handle_rate_limiting()
        
        try:
            async with self.session.get(
                f"{self.config.base_url}/search/products",
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            raise QueryException(f"Product query failed: {str(e)}")

class ShopeeQueryManager:
    """Manager class for handling different types of Shopee queries"""
    
    def __init__(self, config: ShopeeQueryConfig, nlp_processor: Any):
        self.config = config
        self.pipeline = ShopeeQueryPipeline(nlp_processor)
        self.product_query = ShopeeProductQuery(config, nlp_processor)
    
    async def process_query(
        self,
        query_text: str,
        context: QueryContext,
        **kwargs
    ) -> Dict[str, Any]:
        """Process and execute queries with NLP pipeline"""
        try:
            # Validate query
            self._validate_query(query_text)
            
            # Process through NLP pipeline
            nlp_result = await self.pipeline.process(query_text, context)
            
            # Execute appropriate query based on intent
            if nlp_result["intent"] == QueryIntent.PRODUCT_SEARCH.value:
                async with self.product_query as query:
                    results = await query.execute_query({
                        "keywords": query_text,
                        **kwargs
                    })
                    return {**nlp_result, "results": results}
            
            return nlp_result
            
        except QueryException as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception("Unexpected error in query processing")
            raise QueryException(f"Query processing failed: {str(e)}")

    def _validate_query(self, query_text: str) -> None:
        if not query_text.strip():
            raise QueryException("Empty query text", "EMPTY_QUERY")
        if len(query_text) > self.config.max_query_length:
            raise QueryException(
                f"Query exceeds maximum length of {self.config.max_query_length}",
                "QUERY_TOO_LONG"
            )

async def main():
    """Example usage of the ShopeeQueryManager"""
    config = ShopeeQueryConfig(
        base_url="https://api.shopee.com/v2",
        api_key="your_api_key_here"
    )
    
    # Initialize with your NLP processor
    nlp_processor = None  # Replace with actual NLP processor
    query_manager = ShopeeQueryManager(config, nlp_processor)
    
    context = QueryContext(
        user_id="user123",
        session_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow()
    )
    
    try:
        results = await query_manager.process_query(
            query_text="smartphone samsung galaxy",
            context=context,
            category_id=1234,
            page=1,
            limit=20
        )
        print(json.dumps(results, indent=2))
    except QueryException as e:
        logger.error(f"Query failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
