from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from decimal import Decimal
import logging
from enum import Enum
import json
from datetime import datetime
from abc import ABC, abstractmethod

# Data Classes for better type safety and structure
@dataclass
class Product:
    id: str
    name: str
    price: Decimal
    description: str
    category: str
    created_at: datetime
    updated_at: datetime
    stock: int
    status: str

@dataclass
class PriceComparison:
    marketplace: str
    price: Decimal
    last_updated: datetime
    url: str

class ProductStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"

class DatabaseInterface(ABC):
    @abstractmethod
    def get_product(self, product_id: str) -> Optional[Product]:
        pass

    @abstractmethod
    def update_product(self, product: Product) -> bool:
        pass

class ProductDatabase:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self._load_products()
        
    def _load_products(self) -> None:
        """Initialize products from a data source"""
        try:
            # In production, this would load from a real database
            self.products = {
                "smartphone": Product(
                    id="prod_001",
                    name="Smartphone X",
                    price=Decimal("2999.90"),
                    description="Smartphone com 128GB, câmera tripla e tela OLED.",
                    category="eletrônicos",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    stock=100,
                    status=ProductStatus.ACTIVE.value
                ),
                # Add more products...
            }
        except Exception as e:
            self.logger.error(f"Failed to load products: {str(e)}")
            raise

    def get_product_info(self, query: str) -> Dict[str, Any]:
        """Get product information based on search query"""
        try:
            self.logger.info(f"Searching for product with query: {query}")
            for key, product in self.products.items():
                if key in query.lower():
                    return self._product_to_dict(product)
            return {"error": "Product not found", "status": 404}
        except Exception as e:
            self.logger.error(f"Error fetching product info: {str(e)}")
            return {"error": "Internal server error", "status": 500}

    def compare_prices(self, query: str) -> List[PriceComparison]:
        """Compare prices across different marketplaces"""
        try:
            base_product = self.get_product_info(query)
            if "error" in base_product:
                return [PriceComparison(
                    marketplace="Error",
                    price=Decimal("0"),
                    last_updated=datetime.now(),
                    url=""
                )]

            # In production, this would call external APIs
            marketplaces = [
                ("Amazon", "amazon.com"),
                ("Mercado Livre", "mercadolivre.com"),
                ("Kabum", "kabum.com.br"),
                ("Submarino", "submarino.com.br")
            ]

            return [
                PriceComparison(
                    marketplace=name,
                    price=Decimal(str(base_product["price"])),
                    last_updated=datetime.now(),
                    url=f"https://{url}/product/{base_product['id']}"
                )
                for name, url in marketplaces
            ]
        except Exception as e:
            self.logger.error(f"Error comparing prices: {str(e)}")
            return []

    def get_recommendations(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get personalized product recommendations"""
        try:
            category = preferences.get("category", "eletrônicos")
            user_price_range = preferences.get("price_range", (0, float("inf")))
            
            recommendations = [
                product for product in self.products.values()
                if product.category == category
                and user_price_range[0] <= float(product.price) <= user_price_range[1]
            ]
            
            return [self._product_to_dict(product) for product in recommendations[:5]]
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}")
            return []

    @staticmethod
    def _product_to_dict(product: Product) -> Dict[str, Any]:
        """Convert Product object to dictionary"""
        return {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "description": product.description,
            "category": product.category,
            "status": product.status,
            "stock": product.stock,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }

    def to_json(self) -> str:
        """Serialize database to JSON"""
        return json.dumps({
            k: self._product_to_dict(v)
            for k, v in self.products.items()
        })
# chatbots/product_database.py
class ProductDatabase:
    def get_product_info(self, query: str) -> dict:
        return {"name": "Produto Exemplo", "price": "R$ 99,90", "description": query}

    def compare_prices(self, query: str) -> list:
        return [{"store": "Loja A", "price": 90}, {"store": "Loja B", "price": 92}]

    def get_recommendations(self, profile: dict) -> list:
        return ["Produto A", "Produto B"]

    def get_related(self, context: dict) -> list:
        return ["Produto Similar 1", "Produto Similar 2"]
