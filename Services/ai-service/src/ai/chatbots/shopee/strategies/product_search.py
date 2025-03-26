"""
product_search.py
Strategy for handling product searches on Shopee platform.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class to represent search results"""
    products: List[Dict[str, Any]]
    total_count: int
    search_query: str
    source: str = "shopee"

class SearchStrategy(ABC):
    """Abstract base class for search strategies"""
    @abstractmethod
    def search(self, keywords: List[str]) -> SearchResult:
        """Abstract method to be implemented by concrete strategies"""
        pass

class ProductSearchStrategy:
    """
    Handles product search queries by interfacing with SalesDatabase.
    Implements error handling, logging, and result validation.
    """

    def __init__(self, sales_db, max_results: int = 50):
        """
        Initialize the search strategy with dependencies
        
        Args:
            sales_db: Database interface for product searches
            max_results: Maximum number of results to return
        """
        self._sales_db = sales_db
        self._max_results = max_results
        self._default_response = {
            "response": "Não encontrei produtos relacionados. Pode fornecer mais detalhes?",
            "products": [],
            "strategy": "product_search"
        }

    def _validate_input(self, user_id: str, message_text: str, query_info: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        return bool(user_id and message_text and isinstance(query_info, dict))

    def _extract_keywords(self, query_info: Dict[str, Any]) -> List[str]:
        """Extract and clean search keywords"""
        return [
            keyword.strip().lower()
            for keyword in query_info.get("entities", [])
            if keyword and isinstance(keyword, str)
        ]

    def _format_response(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format the search response"""
        if not products:
            return self._default_response

        return {
            "response": f"Encontrei {len(products)} produtos na Shopee que podem te interessar.",
            "products": products[:self._max_results],
            "strategy": "product_search",
            "total_results": len(products)
        }

    async def execute(self, user_id: str, message_text: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the product search strategy
        
        Args:
            user_id: Unique identifier for the user
            message_text: Original search query text
            query_info: Additional query parameters and entities
            
        Returns:
            Dict containing search results and metadata
            
        Raises:
            ValueError: If input parameters are invalid
        """
        try:
            if not self._validate_input(user_id, message_text, query_info):
                raise ValueError("Invalid input parameters")

            logger.info(f"[ProductSearchStrategy] Processing search for user_id={user_id}")
            logger.debug(f"Search query: '{message_text}', info: {query_info}")

            keywords = self._extract_keywords(query_info)
            if not keywords:
                return self._default_response

            products = await self._sales_db.search_products(keywords)
            return self._format_response(products)

        except Exception as e:
            logger.error(f"Error processing product search: {str(e)}", exc_info=True)
            return {
                **self._default_response,
                "error": "Ocorreu um erro ao processar sua busca. Tente novamente."
            }

