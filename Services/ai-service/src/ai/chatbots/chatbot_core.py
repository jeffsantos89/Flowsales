from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import uuid

class Message:
    def __init__(self, content: str, sender_id: str, timestamp: Optional[datetime] = None):
        self.id = str(uuid.uuid4())
        self.content = content
        self.sender_id = sender_id
        self.timestamp = timestamp or datetime.utcnow()

class ChatbotResponse:
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.id = str(uuid.uuid4())
        self.content = content
        self.timestamp = datetime.utcnow()
        self.metadata = metadata or {}

class ChatbotCore(ABC):
    """
    Core abstrato de chatbots para múltiplas plataformas.
    Implementa padrão Template Method para processamento de mensagens.
    """
    def __init__(self, platform: str, config: Optional[Dict[str, Any]] = None):
        self.platform = platform
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configura o sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    @abstractmethod
    def _validate_message(self, message: Message) -> bool:
        """Valida a mensagem recebida."""
        pass

    @abstractmethod
    def _preprocess_message(self, message: Message) -> Message:
        """Pré-processa a mensagem antes do processamento principal."""
        pass

    @abstractmethod
    def _generate_response(self, message: Message) -> ChatbotResponse:
        """Gera a resposta para a mensagem."""
        pass

    def process_message(self, content: str, sender_id: str) -> ChatbotResponse:
        """
        Processa a mensagem seguindo um pipeline definido.
        """
        try:
            # Cria objeto de mensagem
            message = Message(content=content, sender_id=sender_id)
            
            # Registra recebimento
            self.logger.info(f"Received message: {message.id} from {sender_id}")

            # Valida mensagem
            if not self._validate_message(message):
                raise ValueError("Invalid message")

            # Pré-processa
            processed_message = self._preprocess_message(message)

            # Gera resposta
            response = self._generate_response(processed_message)

            # Registra resposta
            self.logger.info(f"Generated response: {response.id}")

            return response

        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return ChatbotResponse(
                content="Desculpe, ocorreu um erro ao processar sua mensagem.",
                metadata={"error": str(e)}
            )

    def __repr__(self) -> str:
        return f"ChatbotCore(platform='{self.platform}')"
