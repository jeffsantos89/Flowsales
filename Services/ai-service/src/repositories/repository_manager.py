from typing import Dict, Type
from functools import lru_cache
from repositories.audit_repository import AuditRepository
from repositories.chatbot_repository import ChatbotRepository
from repositories.error_repository import ErrorRepository
from repositories.marketplace_repository import MarketplaceRepository
from repositories.recommendations_repository import RecommendationsRepository
from repositories.sales_repository import SalesRepository
from repositories.social_media_repository import SocialMediaRepository
from repositories.user_repository import UserRepository
from repositories.whatsapp_repository import WhatsappRepository

class RepositoryManager:
    """
    Singleton class that manages all repository instances using dependency injection.
    """
    _instance = None
    _repositories: Dict[str, object] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._repositories:
            self._initialize_repositories()

    @lru_cache(maxsize=None)
    def _initialize_repositories(self) -> None:
        """Initialize all repository instances with lazy loading"""
        self._repository_classes = {
            'audit': AuditRepository,
            'chatbot': ChatbotRepository,
            'error': ErrorRepository,
            'marketplace': MarketplaceRepository,
            'recommendations': RecommendationsRepository,
            'sales': SalesRepository,
            'social': SocialMediaRepository,
            'user': UserRepository,
            'whatsapp': WhatsappRepository
        }

    def get_repository(self, repository_name: str) -> object:
        """
        Get repository instance using lazy initialization
        """
        if repository_name not in self._repositories:
            if repository_name not in self._repository_classes:
                raise KeyError(f"Repository {repository_name} not found")
            self._repositories[repository_name] = self._repository_classes[repository_name]()
        return self._repositories[repository_name]

    @property
    def audit(self) -> AuditRepository:
        return self.get_repository('audit')

    @property
    def chatbot(self) -> ChatbotRepository:
        return self.get_repository('chatbot')

    @property
    def error(self) -> ErrorRepository:
        return self.get_repository('error')

    @property
    def marketplace(self) -> MarketplaceRepository:
        return self.get_repository('marketplace')

    @property
    def recommendations(self) -> RecommendationsRepository:
        return self.get_repository('recommendations')

    @property
    def sales(self) -> SalesRepository:
        return self.get_repository('sales')

    @property
    def social(self) -> SocialMediaRepository:
        return self.get_repository('social')

    @property
    def user(self) -> UserRepository:
        return self.get_repository('user')

    @property
    def whatsapp(self) -> WhatsappRepository:
        return self.get_repository('whatsapp')

# Global instance with thread-safe initialization
repositories = RepositoryManager()
