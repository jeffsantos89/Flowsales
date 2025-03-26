from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import re
from enum import Enum

logger = logging.getLogger(__name__)

class InquiryStatus(Enum):
    SUCCESS = "success"
    NEED_CLARIFICATION = "need_clarification"
    ERROR = "error"
    NO_MATCHES = "no_matches"

@dataclass(frozen=True)
class ProductInquiry:
    """Immutable data class to store product inquiry details"""
    product_name: str
    customer_id: str
    timestamp: datetime
    query_text: str
    confidence_score: float
    extracted_attributes: Dict[str, Any]
    session_id: str  # Added for tracking
    platform: str    # Added for multi-platform support

class ProductMatchResult:
    """Value object for product matching results"""
    def __init__(self, 
                 products: List[Dict],
                 confidence: float,
                 match_criteria: Dict[str, Any]):
        self.products = products
        self.confidence = confidence
        self.match_criteria = match_criteria

class ProductInquiryStrategy(ABC):
    """Abstract base class for product inquiry strategies"""
    @abstractmethod
    def handle_inquiry(self, message: str, context: Dict) -> Dict:
        pass

    @abstractmethod
    def can_handle(self, platform: str) -> bool:
        """Check if strategy can handle given platform"""
        pass

class InstagramProductInquiryStrategy(ProductInquiryStrategy):
    """Strategy for handling product inquiries from Instagram"""
    
    PLATFORM = "instagram"
    
    def __init__(self, 
                 product_catalog: Dict,
                 threshold: float = 0.7,
                 max_history_size: int = 1000):
        self.product_catalog = product_catalog
        self.confidence_threshold = threshold
        self.inquiry_history: List[ProductInquiry] = []
        self.max_history_size = max_history_size
        self._setup_nlp()

    def _setup_nlp(self) -> None:
        """Initialize NLP components"""
        # Here you would initialize your NLP models, tokenizers, etc.
        pass

    def can_handle(self, platform: str) -> bool:
        return platform.lower() == self.PLATFORM

    def handle_inquiry(self, message: str, context: Dict) -> Dict:
        """Main inquiry handling method with error handling and logging"""
        try:
            with self._create_inquiry_context(context) as ctx:
                cleaned_message = self._sanitize_input(message)
                product_info = self._extract_product_info(cleaned_message)
                
                if not self._validate_inquiry(product_info):
                    return self._create_response(InquiryStatus.NEED_CLARIFICATION)

                match_result = self._match_products(product_info)
                inquiry = self._create_inquiry_record(message, ctx, product_info)
                self._update_history(inquiry)

                return self._generate_response(match_result, inquiry)

        except Exception as e:
            logger.error(f"Error processing inquiry: {str(e)}", exc_info=True)
            return self._create_response(InquiryStatus.ERROR)

    def _create_inquiry_context(self, context: Dict) -> Any:
        """Context manager for inquiry processing"""
        from contextlib import contextmanager
        
        @contextmanager
        def inquiry_context(ctx):
            start_time = datetime.now()
            try:
                ctx['session_id'] = ctx.get('session_id', str(start_time.timestamp()))
                yield ctx
            finally:
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Inquiry processing took {duration}s")
                
        return inquiry_context(context)

    def _update_history(self, inquiry: ProductInquiry) -> None:
        """Update inquiry history with size limit"""
        self.inquiry_history.append(inquiry)
        if len(self.inquiry_history) > self.max_history_size:
            self.inquiry_history = self.inquiry_history[-self.max_history_size:]

    def _match_products(self, product_info: Dict) -> ProductMatchResult:
        """Enhanced product matching with scoring"""
        matched_products = []
        match_scores = {}
        
        for product_id, product in self.product_catalog.items():
            score = self._calculate_match_score(product_info, product)
            if score > self.confidence_threshold:
                matched_products.append({
                    "product_id": product_id,
                    "details": product,
                    "match_score": score
                })
                match_scores[product_id] = score

        return ProductMatchResult(
            products=sorted(matched_products, key=lambda x: x["match_score"], reverse=True),
            confidence=max(match_scores.values()) if match_scores else 0.0,
            match_criteria=product_info
        )

    def _calculate_match_score(self, product_info: Dict, product: Dict) -> float:
        """Calculate match score between inquiry and product"""
        # Implement sophisticated matching logic here
        # Could use text similarity, attribute matching, etc.
        return 0.8  # Placeholder

    def _create_response(self, status: InquiryStatus, **kwargs) -> Dict:
        """Unified response creation"""
        response = {
            "status": status.value,
            "timestamp": datetime.now().isoformat()
        }
        response.update(kwargs)
        return response

    def _generate_response(self, 
                         match_result: ProductMatchResult, 
                         inquiry: ProductInquiry) -> Dict:
        """Generate response based on match results"""
        if not match_result.products:
            return self._create_response(
                InquiryStatus.NO_MATCHES,
                suggested_alternatives=self._get_alternative_suggestions(inquiry)
            )

        return self._create_response(
            InquiryStatus.SUCCESS,
            products=match_result.products,
            confidence=match_result.confidence,
            suggested_actions=self._get_suggested_actions(match_result.products),
            analysis=self._get_response_analysis(match_result)
        )

    def _get_alternative_suggestions(self, inquiry: ProductInquiry) -> List[Dict]:
        """Generate alternative product suggestions"""
        # Implement suggestion logic here
        return []

    def _get_response_analysis(self, match_result: ProductMatchResult) -> Dict:
        """Provide detailed analysis of the matching process"""
        return {
            "match_criteria": match_result.match_criteria,
            "confidence_breakdown": {
                "overall": match_result.confidence,
                "attributes": {}  # Add attribute-specific confidence scores
            }
        }
