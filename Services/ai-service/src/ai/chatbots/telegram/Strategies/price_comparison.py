"""
price_comparison.py
Price comparison strategy implementation with advanced features and robust error handling.
"""

from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceComparisonError(Exception):
    """Custom exception for price comparison errors"""
    pass

class ComparisonType(Enum):
    HISTORICAL = "historical"
    COMPETITOR = "competitor"
    COMBINED = "combined"

@dataclass
class PriceData:
    product_id: str
    price: float
    timestamp: datetime
    seller: str
    currency: str = "BRL"

class PriceComparator(ABC):
    @abstractmethod
    def compare(self, product_id: str) -> Dict[str, Any]:
        pass

class StandardPriceComparator(PriceComparator):
    def __init__(self, sales_db):
        self.sales_db = sales_db

    def compare(self, product_id: str) -> Dict[str, Any]:
        return self.sales_db.compare_prices(product_id)

class PriceComparisonStrategy:
    def __init__(self, sales_db, comparator: Optional[PriceComparator] = None):
        """
        Initialize the price comparison strategy.
        
        Args:
            sales_db: Database connection instance
            comparator: Optional custom price comparator
        """
        self.sales_db = sales_db
        self.comparator = comparator or StandardPriceComparator(sales_db)
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    def _validate_input(self, user_id: str, query_info: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        if not user_id or not isinstance(user_id, str):
            raise ValueError("Invalid user_id")
        if not query_info or not isinstance(query_info, dict):
            raise ValueError("Invalid query_info")
        return True

    def _extract_product_id(self, query_info: Dict[str, Any]) -> str:
        """Extract product ID from query info"""
        product_id = query_info.get("product_id")
        if not product_id:
            raise PriceComparisonError("Product ID not found in query")
        return product_id

    def _format_response(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the response with price comparison data"""
        try:
            return {
                "response": "Here are the compared prices:",
                "comparison": price_data,
                "strategy": "price_comparison",
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            raise PriceComparisonError("Error formatting response")

    async def execute(self, user_id: str, message_text: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the price comparison strategy.
        
        Args:
            user_id: User identifier
            message_text: Original message text
            query_info: Additional query information
            
        Returns:
            Dict containing comparison results
            
        Raises:
            PriceComparisonError: If comparison fails
        """
        try:
            logger.info(f"[PriceComparisonStrategy] Executing for user={user_id}")
            
            # Validate inputs
            self._validate_input(user_id, query_info)
            
            # Extract product ID
            product_id = self._extract_product_id(query_info)
            
            # Check cache
            cache_key = f"{product_id}:{user_id}"
            if cache_key in self.cache:
                logger.info(f"Returning cached result for {cache_key}")
                return self.cache[cache_key]
            
            # Get price comparison
            price_data = self.comparator.compare(product_id)
            
            if not price_data:
                logger.warning(f"No price data found for product_id={product_id}")
                return {
                    "response": "Unable to compare prices at this time.",
                    "strategy": "price_comparison",
                    "status": "no_data"
                }
            
            # Format and cache response
            response = self._format_response(price_data)
            self.cache[cache_key] = response
            
            return response

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise PriceComparisonError(f"Invalid input: {str(e)}")
        except Exception as e:
            logger.error(f"Error executing price comparison: {str(e)}")
            raise PriceComparisonError(f"Price comparison failed: {str(e)}")
