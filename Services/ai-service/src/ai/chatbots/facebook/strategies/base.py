"""
base.py
Define a classe base para estratégias de tratamento de mensagens no Messenger.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Enum para tipos de mensagens suportadas"""
    TEXT = "text"
    QUICK_REPLY = "quick_reply"
    POSTBACK = "postback"
    ATTACHMENT = "attachment"
    UNKNOWN = "unknown"

@dataclass
class ProcessingResult:
    """Classe para encapsular o resultado do processamento"""
    success: bool
    message: Dict[str, Any]
    error: Optional[str] = None
    processed_at: datetime = datetime.now()

class BaseFacebookStrategy(ABC):
    """
    Classe base abstrata para estratégias de mensagem do Messenger.
    Cada estratégia (text, quick reply, postback) deve implementar process() e retornar a saída apropriada.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def process(self, message_payload: Dict[str, Any]) -> ProcessingResult:
        """
        Recebe o payload da mensagem e retorna um ProcessingResult com o resultado do processamento.

        Args:
            message_payload: Dicionário contendo o payload da mensagem do Facebook

        Returns:
            ProcessingResult: Objeto contendo o resultado do processamento

        Raises:
            ValueError: Se o payload estiver mal formatado
            Exception: Para outros erros durante o processamento
        """
        pass

    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Valida se o payload possui a estrutura necessária.

        Args:
            payload: Dicionário com o payload a ser validado

        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            if not isinstance(payload, dict):
                return False
            if not payload.get("sender") or not payload.get("recipient"):
                return False
            return True
        except Exception as e:
            self.logger.error(f"Erro na validação do payload: {str(e)}")
            return False

    def get_message_type(self, payload: Dict[str, Any]) -> MessageType:
        """
        Determina o tipo da mensagem baseado no payload.

        Args:
            payload: Dicionário com o payload da mensagem

        Returns:
            MessageType: Enum indicando o tipo da mensagem
        """
        if "message" in payload:
            if "quick_reply" in payload["message"]:
                return MessageType.QUICK_REPLY
            elif "text" in payload["message"]:
                return MessageType.TEXT
            elif "attachments" in payload["message"]:
                return MessageType.ATTACHMENT
        elif "postback" in payload:
            return MessageType.POSTBACK
        return MessageType.UNKNOWN

    def create_error_response(self, error_message: str) -> ProcessingResult:
        """
        Cria uma resposta padrão para erros.

        Args:
            error_message: Mensagem de erro

        Returns:
            ProcessingResult: Objeto com informações do erro
        """
        return ProcessingResult(
            success=False,
            message={"text": "Desculpe, ocorreu um erro no processamento."},
            error=error_message
        )
