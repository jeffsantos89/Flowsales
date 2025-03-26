from typing import Dict, Optional, List
from datetime import datetime
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
import json
from pathlib import Path
import threading

class Language(Enum):
    EN = 'en'
    PT = 'pt'
    ES = 'es'

@dataclass
class UserContext:
    """Stores user interaction context"""
    user_id: str
    first_interaction: datetime
    language: Language = Language.EN
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    metadata: Dict = None

    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'first_interaction': self.first_interaction.isoformat(),
            'language': self.language.value,
            'interaction_count': self.interaction_count,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserContext':
        return cls(
            user_id=data['user_id'],
            first_interaction=datetime.fromisoformat(data['first_interaction']),
            language=Language(data['language']),
            interaction_count=data['interaction_count'],
            last_interaction=datetime.fromisoformat(data['last_interaction']) if data['last_interaction'] else None,
            metadata=data.get('metadata', {})
        )

class WelcomeMessageStrategy(ABC):
    @abstractmethod
    def generate_message(self, user_context: UserContext) -> str:
        pass

class TimeBasedWelcomeStrategy(WelcomeMessageStrategy):
    _messages = {
        Language.EN: {
            'morning': 'Good morning! Welcome to our service.',
            'afternoon': 'Good afternoon! Welcome to our service.',
            'evening': 'Good evening! Welcome to our service.'
        },
        Language.PT: {
            'morning': 'Bom dia! Bem-vindo ao nosso serviço.',
            'afternoon': 'Boa tarde! Bem-vindo ao nosso serviço.',
            'evening': 'Boa noite! Bem-vindo ao nosso serviço.'
        },
        Language.ES: {
            'morning': '¡Buenos días! Bienvenido a nuestro servicio.',
            'afternoon': '¡Buenas tardes! Bienvenido a nuestro servicio.',
            'evening': '¡Buenas noches! Bienvenido a nuestro servicio.'
        }
    }

    def generate_message(self, user_context: UserContext) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 18:
            period = "afternoon"
        else:
            period = "evening"
        
        return self._messages.get(user_context.language, self._messages[Language.EN])[period]

class InstagramWelcomeHandler:
    """Handles welcome messages for Instagram chat interactions"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._logger = logging.getLogger(__name__)
            self._user_contexts: Dict[str, UserContext] = {}
            self._welcome_strategy: WelcomeMessageStrategy = TimeBasedWelcomeStrategy()
            self._max_retries = 3
            self._storage_path = Path('data/user_contexts.json')
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._lock = threading.Lock()
            self._load_contexts()
            self._initialized = True
        
    def _load_contexts(self) -> None:
        """Loads user contexts from persistent storage"""
        try:
            if self._storage_path.exists():
                with open(self._storage_path, 'r') as f:
                    data = json.load(f)
                    self._user_contexts = {
                        k: UserContext.from_dict(v) for k, v in data.items()
                    }
        except Exception as e:
            self._logger.error(f"Error loading user contexts: {e}", exc_info=True)

    def _save_contexts(self) -> None:
        """Saves user contexts to persistent storage"""
        try:
            with open(self._storage_path, 'w') as f:
                json.dump({
                    k: v.to_dict() for k, v in self._user_contexts.items()
                }, f, indent=2)
        except Exception as e:
            self._logger.error(f"Error saving user contexts: {e}", exc_info=True)

    def set_strategy(self, strategy: WelcomeMessageStrategy) -> None:
        with self._lock:
            self._welcome_strategy = strategy
            
    def get_welcome_message(self, user_id: str, metadata: Optional[Dict] = None) -> str:
        try:
            with self._lock:
                user_context = self._user_contexts.get(
                    user_id, 
                    self._create_user_context(user_id)
                )
                
                user_context.interaction_count += 1
                user_context.last_interaction = datetime.now()
                
                if metadata:
                    if 'language' in metadata:
                        try:
                            user_context.language = Language(metadata['language'])
                        except ValueError:
                            self._logger.warning(f"Invalid language: {metadata['language']}")
                    user_context.metadata = dict(**user_context.metadata or {}, **metadata)
                
                self._user_contexts[user_id] = user_context
                self._save_contexts()
                
                welcome_message = self._welcome_strategy.generate_message(user_context)
                
                self._logger.info(
                    "Welcome message generated",
                    extra={
                        "user_id": user_id,
                        "interaction_count": user_context.interaction_count,
                        "language": user_context.language.value
                    }
                )
                
                return welcome_message
                
        except Exception as e:
            self._logger.error(
                f"Error generating welcome message: {str(e)}",
                extra={"user_id": user_id},
                exc_info=True
            )
            return "Welcome! How can I help you today?"

    def _create_user_context(self, user_id: str) -> UserContext:
        return UserContext(
            user_id=user_id,
            first_interaction=datetime.now()
        )
            
    def cleanup_old_contexts(self, days: int = 30) -> None:
        with self._lock:
            threshold = datetime.now().timestamp() - (days * 24 * 60 * 60)
            old_contexts = [
                user_id for user_id, context in self._user_contexts.items()
                if context.last_interaction and context.last_interaction.timestamp() < threshold
            ]
            for user_id in old_contexts:
                self._user_contexts.pop(user_id)
            self._save_contexts()
            
    def get_active_users_count(self) -> int:
        return len(self._user_contexts)

# Singleton instance
welcome_handler = InstagramWelcomeHandler()
