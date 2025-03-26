"""
product_search.py
Product search strategy implementation with robust error handling and validation.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re
from database.sales import SalesDatabase  # Import the SalesDatabase class

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class to represent search results"""
    products: List[Dict[str, Any]]
    total_count: int
    query_time: float
    search_criteria: Dict[str, Any]

class SearchStrategy(ABC):
    """Abstract base class for search strategies"""
    @abstractmethod
    def execute(self, user_id: str, message_text: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
        pass

class ProductSearchStrategy(SearchStrategy):
    """Implementation of product search strategy with enhanced features"""
    
    MAX_RESULTS = 50
    MIN_KEYWORD_LENGTH = 2
    
    def __init__(self, sales_db: 'SalesDatabase'):
        """Initialize the strategy with database connection"""
        self.sales_db = sales_db
        self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        """Validate all required dependencies"""
        if not self.sales_db:
            raise ValueError("Sales database connection is required")

    def _sanitize_keywords(self, keywords: List[str]) -> List[str]:
        """Clean and validate keywords"""
        return [
            k.strip().lower() 
            for k in keywords 
            if isinstance(k, str) and len(k.strip()) >= self.MIN_KEYWORD_LENGTH
        ]

    def _validate_input(self, user_id: str, message_text: str, query_info: Dict[str, Any]) -> None:
        """Validate input parameters"""
        if not user_id:
            raise ValueError("User ID is required")
        if not message_text:
            raise ValueError("Message text cannot be empty")
        if not isinstance(query_info, dict):
            raise TypeError("Query info must be a dictionary")

    def _extract_keywords(self, message_text: str, query_info: Dict[str, Any]) -> List[str]:
        """Extract keywords from message and query info"""
        keywords = query_info.get("entities", [])
        
        # If no keywords in entities, extract from message text
        if not keywords:
            # Simple keyword extraction (could be enhanced with NLP)
            keywords = [word for word in re.split(r'\W+', message_text) 
                       if len(word) >= self.MIN_KEYWORD_LENGTH]
        
        return self._sanitize_keywords(keywords)

    def execute(self, user_id: str, message_text: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the product search strategy"""
        try:
            # Input validation
            self._validate_input(user_id, message_text, query_info)
            
            # Log operation start
            logger.info(f"[ProductSearchStrategy] Starting search for user={user_id}")
            logger.debug(f"Search parameters: text='{message_text}', query_info={query_info}")

            # Extract and process keywords
            keywords = self._extract_keywords(message_text, query_info)
            
            if not keywords:
                return {
                    "response": "Por favor, forneça mais detalhes para a busca.",
                    "strategy": "product_search",
                    "status": "no_keywords"
                }

            # Perform search with pagination and limits
            try:
                products = self.sales_db.search_products(
                    keywords,
                    limit=self.MAX_RESULTS,
                    offset=query_info.get("offset", 0)
                )
            except Exception as e:
                logger.error(f"Database search failed: {str(e)}")
                raise

            # Process results
            if not products:
                return {
                    "response": "Não encontrei produtos relacionados. Pode especificar melhor?",
                    "strategy": "product_search",
                    "status": "no_results",
                    "search_terms": keywords
                }

            # Return successful response
            return {
                "response": f"Encontrei {len(products)} produtos para você.",
                "products": products,
                "strategy": "product_search",
                "status": "success",
                "search_terms": keywords,
                "has_more": len(products) == self.MAX_RESULTS
            }

        except ValueError as ve:
            logger.warning(f"Validation error: {str(ve)}")
            return {"response": str(ve), "strategy": "product_search", "status": "error"}
        
        except Exception as e:
            logger.error(f"Unexpected error in product search: {str(e)}", exc_info=True)
            return {
                "response": "Desculpe, ocorreu um erro ao processar sua busca.",
                "strategy": "product_search",
                "status": "error"
            }
