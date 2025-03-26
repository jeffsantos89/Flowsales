import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import asyncio
from enum import Enum
from decimal import Decimal
from functools import wraps
import json
from time import time

logger = logging.getLogger(__name__)

class ProductStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

@dataclass(frozen=True)
class Product:
    id: int
    name: str
    price: Decimal
    category: str
    sku: str
    description: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    stock: int = 0
    status: ProductStatus = ProductStatus.ACTIVE

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'price': str(self.price),
            'category': self.category,
            'sku': self.sku,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'stock': self.stock,
            'status': self.status.value
        }

def cache_decorator(ttl_seconds: int = 3600):
    def decorator(func):
        cache = {}
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            now = time()
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if now - timestamp < ttl_seconds:
                    return result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, now)
            return result
        return wrapper
    return decorator

class DatabaseInterface(ABC):
    @abstractmethod
    async def search_products(self, query: str) -> List[Product]:
        pass

    @abstractmethod
    async def get_product_info(self, product_id: int) -> Optional[Product]:
        pass

    @abstractmethod
    async def compare_prices(self, product_id: int) -> Dict:
        pass

    @abstractmethod
    async def get_recommendations(self, user_id: str, limit: int) -> List[Product]:
        pass

class SalesDatabase(DatabaseInterface):
    def __init__(self, cache_ttl: int = 3600):
        self._cache_ttl = cache_ttl
        self._products = self._initialize_products()
        self._lock = asyncio.Lock()
        self._max_retries = 3
        self._retry_delay = 1  # seconds

    def _initialize_products(self) -> List[Product]:
        # In production, this would load from a real database
        return [
            Product(
                id=1,
                name="Fone Bluetooth",
                price=Decimal('199.90'),
                category="Áudio",
                sku="FON-BT-001",
                description="Fone de ouvido bluetooth com cancelamento de ruído",
                stock=100,
                status=ProductStatus.ACTIVE
            ),
        ]

    async def _retry_operation(self, operation):
        for attempt in range(self._max_retries):
            try:
                return await operation()
            except Exception as e:
                if attempt == self._max_retries - 1:
                    raise
                logger.warning(f"Operation failed, retrying... ({attempt + 1}/{self._max_retries})")
                await asyncio.sleep(self._retry_delay * (attempt + 1))

    @cache_decorator(ttl_seconds=3600)
    async def search_products(self, query: str) -> List[Product]:
        async def _search():
            async with self._lock:
                query_lower = query.lower()
                return [
                    p for p in self._products 
                    if query_lower in p.name.lower() or 
                    (p.description and query_lower in p.description.lower())
                ]
        return await self._retry_operation(_search)

    @cache_decorator(ttl_seconds=1800)
    async def get_product_info(self, product_id: int) -> Optional[Product]:
        async def _get_product():
            return next(
                (p for p in self._products if p.id == product_id),
                None
            )
        return await self._retry_operation(_get_product)

    async def compare_prices(self, product_id: int) -> Dict:
        async def _compare():
            product = await self.get_product_info(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")

            competitor_prices = await self._fetch_competitor_prices(product_id)
            
            analysis = {
                "product": product.to_dict(),
                "our_price": float(product.price),
                "competitor_prices": competitor_prices,
                "average_market_price": sum(p['price'] for p in competitor_prices) / len(competitor_prices),
                "is_competitive": float(product.price) <= min(p['price'] for p in competitor_prices),
                "analysis_timestamp": datetime.now().isoformat()
            }
            return analysis

        return await self._retry_operation(_compare)

    async def _fetch_competitor_prices(self, product_id: int) -> List[Dict]:
        # Mock implementation - in production, integrate with real APIs
        async def _fetch():
            await asyncio.sleep(0.1)
            return [
                {"competitor": "Competitor A", "price": 219.90},
                {"competitor": "Competitor B", "price": 209.90}
            ]
        return await self._retry_operation(_fetch)

    @cache_decorator(ttl_seconds=1800)
    async def get_recommendations(self, user_id: str, limit: int = 5) -> List[Product]:
        async def _get_recommendations():
            # Mock implementation - in production, use a proper recommendation engine
            active_products = [p for p in self._products if p.status == ProductStatus.ACTIVE]
            return sorted(active_products, key=lambda p: p.stock)[:limit]
        
        return await self._retry_operation(_get_recommendations)

    def clear_cache(self):
        # In a real implementation, this would clear distributed cache
        for attr in dir(self):
            if hasattr(getattr(self, attr), 'cache'):
                getattr(self, attr).cache.clear()
