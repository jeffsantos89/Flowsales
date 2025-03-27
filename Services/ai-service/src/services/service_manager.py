# src/services/service_manager.py
from typing import Dict, Type, Any
from functools import lru_cache
from abc import ABC

# Import services
from services.auth_service import AuthService
from services.event_service import EventService
from services.marketplace_service import MarketplaceService
from services.model_service import ModelService
from services.predict_service import PredictService
from services.recommendations_service import RecommendationsService
from services.sales_forecast_service import SalesForecastService
from services.security_service import SecurityService
from services.social_media_service import SocialMediaService
from services.whatsapp_service import WhatsAppService
from services.analytics_service import AnalyticsService
from services.ai_service import AIService

class BaseService(ABC):
    """Base abstract class for all services"""
    pass

class ServiceManager:
    """
    Service Manager implementation using Singleton pattern and lazy loading
    """
    _instance = None
    _services: Dict[str, Any] = {}
    
    _SERVICE_MAPPING = {
        'auth': AuthService,
        'events': EventService,
        'marketplace': MarketplaceService,
        'model': ModelService,
        'predict': PredictService,
        'recommendations': RecommendationsService,
        'forecast': SalesForecastService,
        'security': SecurityService,
        'social': SocialMediaService,
        'whatsapp': WhatsAppService,
        'analytics': AnalyticsService,
        'ai': AIService
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
        return cls._instance

    def __getattr__(self, service_name: str) -> Any:
        """Lazy loading of services"""
        if service_name not in self._services:
            if service_name not in self._SERVICE_MAPPING:
                raise AttributeError(f"Service '{service_name}' not found")
            
            self._services[service_name] = self._SERVICE_MAPPING[service_name]()
        
        return self._services[service_name]

    @classmethod
    def register_service(cls, name: str, service_class: Type[BaseService]) -> None:
        """Register a new service dynamically"""
        cls._SERVICE_MAPPING[name] = service_class

    def get_service(self, service_name: str) -> Any:
        """Get service by name"""
        return getattr(self, service_name)

    @lru_cache()
    def list_available_services(self) -> list:
        """List all available services"""
        return list(self._SERVICE_MAPPING.keys())

    def reset_service(self, service_name: str) -> None:
        """Reset specific service instance"""
        if service_name in self._services:
            del self._services[service_name]

    def reset_all_services(self) -> None:
        """Reset all service instances"""
        self._services.clear()

# Global instance for direct use
services = ServiceManager()

# Prevent further instantiation
ServiceManager.__new__ = lambda cls: services
