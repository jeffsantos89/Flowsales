"""
price_comparison.py
Estratégia de comparação de preços entre diferentes sellers, SKU's ou marketplaces.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
from statistics import mean, median, stdev
import httpx

from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from utils.cache import TTLCache
from .base import BaseAmazonStrategy

class PriceComparisonStrategy(BaseAmazonStrategy):
    def __init__(self, cache: Optional[TTLCache] = None):
        self.cache = cache or TTLCache()
        self.api_endpoint = "https://api.amazon.fake/v1/prices"  # Fictício

    @retry(max_attempts=3, backoff=2)
    @background_task
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload espera: { "product_id": "XYZ123" }
        Retorna: { "lowest_price": float, "highest_price": float, "offers": [...] }
        """
        product_id = payload.get("product_id")
        if not product_id:
            return {"error": "product_id não fornecido"}

        try:
            cache_key = f"price_comp::{product_id}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info("[PriceComparisonStrategy] Retornando dados de cache.")
                return cached_data

            logger.info(f"[PriceComparisonStrategy] Comparando preços para: {product_id}")
            offers = asyncio.run(self._fetch_price_data(product_id))
            result = self._process_offers(offers)

            self.cache.set(cache_key, result)
            return result

        except Exception as e:
            logger.exception("[PriceComparisonStrategy] Erro ao comparar preços")
            return {"error": str(e)}

    async def _fetch_price_data(self, product_id: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(self.api_endpoint, params={"product_id": product_id})
            resp.raise_for_status()
            data = resp.json()
            return data.get("offers", [])

    def _validate_price(self, price: float) -> bool:
        """
        Validates if price is within acceptable bounds and not an absurd value.
        """
        if not isinstance(price, (int, float)):
            return False
            
        MIN_PRICE = 0.01
        MAX_PRICE = 1_000_000.00
        return MIN_PRICE <= price <= MAX_PRICE

    def _sanitize_offers(self, offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cleans and validates offer data, removes invalid entries and normalizes values.
        """
        return [
            {
                'price': round(float(offer['price']), 2),
                'seller': offer.get('seller', '').strip(),
                'condition': offer.get('condition', 'new').lower(),
                'availability': bool(offer.get('availability', True)),
                'marketplace': offer.get('marketplace', 'amazon').lower(),
                'last_updated': offer.get('last_updated'),
                'shipping': offer.get('shipping', 0.0),
                'rating': offer.get('rating', 0.0),
                'reviews_count': offer.get('reviews_count', 0)
            }
            for offer in offers
            if self._validate_price(offer.get('price'))
        ]

    def _get_analytics(self, offers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates advanced price metrics including median, standard deviation and outliers.
        """
        if not offers:
            return {}

        prices = [o['price'] for o in offers]
        avg_price = mean(prices)
        std_dev = stdev(prices) if len(prices) > 1 else 0

        return {
            'median_price': round(median(prices), 2),
            'std_deviation': round(std_dev, 2),
            'price_range': round(max(prices) - min(prices), 2),
            'offers_count': len(offers),
            'unique_sellers': len({o['seller'] for o in offers}),
            'marketplaces': list({o['marketplace'] for o in offers}),
            'outliers': [p for p in prices if abs(p - avg_price) > 2 * std_dev],
            'price_segments': {
                'low': len([p for p in prices if p < avg_price - std_dev]),
                'mid': len([p for p in prices if avg_price - std_dev <= p <= avg_price + std_dev]),
                'high': len([p for p in prices if p > avg_price + std_dev])
            }
        }

    def _process_offers(self, offers: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not offers:
            return {"lowest_price": None, "highest_price": None, "offers": []}

        sanitized_offers = self._sanitize_offers(offers)
        if not sanitized_offers:
            return {"lowest_price": None, "highest_price": None, "offers": []}

        prices = [o['price'] for o in sanitized_offers]
        analytics = self._get_analytics(sanitized_offers)

        return {
            "lowest_price": float(min(prices)),
            "highest_price": float(max(prices)),
            "offers": sanitized_offers,
            "analytics": analytics
        }

    def analyze_market(self, product_id: str) -> Dict[str, Any]:
        """
        Comprehensive market analysis for a product.
        """
        try:
            offers = asyncio.run(self._fetch_price_data(product_id))
            sanitized_offers = self._sanitize_offers(offers)
            analytics = self._get_analytics(sanitized_offers)
            
            best_value_offers = sorted(
                sanitized_offers,
                key=lambda x: (x['quality_score'] * 0.7) - (x['price'] * 0.3),
                reverse=True
            )[:5]

            return {
                'market_analysis': analytics,
                'best_value_offers': best_value_offers,
                'price_trends': {
                    'current_market_position': 'competitive' if analytics['std_deviation'] < analytics['median_price'] * 0.1 else 'volatile',
                    'price_stability_score': round(100 - (analytics['std_deviation'] / analytics['median_price'] * 100), 2)
                },
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'sample_size': len(sanitized_offers),
                    'confidence_score': min(len(sanitized_offers) * 10, 100)
                }
            }
        except Exception as e:
            logger.exception("Error in market analysis")
            raise ValueError(f"Market analysis failed: {str(e)}")
