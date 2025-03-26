"""
Schemas module initialization.
This module exports all schema classes used across the application.
"""

from typing import List, Type

from .marketplace_schema import MarketplaceMessage
from .predict_schema import PredictRequest, PredictResponse
from .recommendations import RecommendationResponse
from .sales_forecast_schema import SalesForecastInput, SalesForecastResult
from .whatsapp_schema import WhatsAppInboundMessage, WhatsAppOutboundMessage

# Define all available schemas
SCHEMAS: List[Type] = [
    MarketplaceMessage,
    PredictRequest,
    PredictResponse,
    RecommendationResponse,
    SalesForecastInput,
    SalesForecastResult,
    WhatsAppInboundMessage,
    WhatsAppOutboundMessage,
]

__all__ = [schema.__name__ for schema in SCHEMAS]

# Version information
__version__ = '1.0.0'
__author__ = 'Flowsale Team'

# Validate all schemas on import
for schema in SCHEMAS:
    if not hasattr(schema, '__annotations__'):
        raise TypeError(f"Schema {schema.__name__} must have type annotations")
