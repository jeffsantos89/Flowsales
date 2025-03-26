# src/ai/nlp/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class AnalysisResult:
    """Estrutura de dados para armazenar o resultado da análise"""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    original_message: str
    processed_at: str
    metadata: Dict[str, Any]

class NLPProcessorException(Exception):
    """Exceção customizada para erros de processamento NLP"""
    pass

class NLPProcessor(ABC):
    def __init__(self, language: str = "pt-BR", min_confidence: float = 0.5):
        self.language = language
        self.min_confidence = min_confidence
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def analyze(self, message: str) -> AnalysisResult:
        """
        Analisa a mensagem e retorna a intenção do usuário
        
        Args:
            message: Texto a ser analisado
            
        Returns:
            AnalysisResult contendo a análise completa
            
        Raises:
            NLPProcessorException: Se houver erro no processamento
        """
        pass

    @abstractmethod
    async def train(self, training_data: Dict[str, Any]) -> bool:
        """
        Treina o modelo com novos dados
        
        Args:
            training_data: Dados de treinamento
            
        Returns:
            bool indicando sucesso do treinamento
        """
        pass

    def validate_message(self, message: str) -> bool:
        """Valida se a mensagem está em formato adequado"""
        if not message or not isinstance(message, str):
            raise NLPProcessorException("Mensagem inválida")
        return True

    def get_confidence_level(self, score: float) -> IntentConfidence:
        """Classifica o nível de confiança da análise"""
        if score < 0.3:
            return IntentConfidence.LOW
        elif score < 0.7:
            return IntentConfidence.MEDIUM
        return IntentConfidence.HIGH
