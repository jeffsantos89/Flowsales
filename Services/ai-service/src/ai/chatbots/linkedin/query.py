"""
query.py
Pipeline de NLP especializada para processamento de mensagens do LinkedIn,
com foco em análise de intenção, extração de entidades e preprocessamento de texto.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
import re
from enum import Enum
from functools import lru_cache

from ai.nlp.huggingface_processor import HuggingFaceProcessor
from ai.exceptions import NLPProcessingError, TextCleaningError

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Enumeração de tipos de intenções possíveis"""
    SALES = "sales"
    MESSAGE = "message"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class NLPResult:
    """Classe para representar o resultado do processamento NLP"""
    intent: IntentType
    entities: List[Dict[str, Any]]
    confidence: float
    cleaned_text: str
    error: Optional[str] = None

class LinkedInQueryPipeline:
    """
    Pipeline avançada de NLP para análise de mensagens do LinkedIn.
    Implementa processamento em cache, validações e limpeza de texto robusta.
    """

    def __init__(
        self, 
        nlp_processor: HuggingFaceProcessor,
        min_confidence: float = 0.7,
        cache_size: int = 1000
    ):
        self.nlp_processor = nlp_processor
        self.min_confidence = min_confidence
        self._initialize_patterns()

    def _initialize_patterns(self) -> None:
        """Inicializa padrões de regex para limpeza de texto"""
        self.patterns = {
            'urls': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'emails': re.compile(r'\S+@\S+'),
            'special_chars': re.compile(r'[^\w\s]'),
            'extra_spaces': re.compile(r'\s+')
        }

    @lru_cache(maxsize=1000)
    def process(self, text: str) -> NLPResult:
        """
        Processa o texto aplicando limpeza, normalização e análise NLP.
        Implementa cache para textos repetidos.

        Args:
            text (str): Texto da mensagem para análise

        Returns:
            NLPResult: Resultado estruturado da análise

        Raises:
            NLPProcessingError: Quando há erro no processamento NLP
            ValueError: Quando o texto está vazio ou inválido
        """
        if not text or not isinstance(text, str):
            raise ValueError("Texto inválido ou vazio")

        try:
            cleaned_text = self._clean_text(text)
            if not cleaned_text:
                return NLPResult(
                    intent=IntentType.UNKNOWN,
                    entities=[],
                    confidence=0.0,
                    cleaned_text=text,
                    error="Texto vazio após limpeza"
                )

            nlp_result = self.nlp_processor.analyze(cleaned_text)
            
            # Validação do resultado
            if not self._validate_nlp_result(nlp_result):
                logger.warning(f"Resultado NLP inválido para texto: {cleaned_text[:100]}")
                return self._create_error_result("Resultado NLP inválido")

            confidence = nlp_result.get("confidence", 0.0)
            intent = self._determine_intent(nlp_result, confidence)
            
            return NLPResult(
                intent=intent,
                entities=self._process_entities(nlp_result.get("entities", [])),
                confidence=confidence,
                cleaned_text=cleaned_text
            )

        except Exception as e:
            logger.exception("[LinkedInQueryPipeline] Erro no processamento")
            raise NLPProcessingError(f"Erro no processamento: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """
        Realiza limpeza avançada do texto com múltiplas etapas de processamento.
        
        Args:
            text (str): Texto original
            
        Returns:
            str: Texto limpo e normalizado
        """
        try:
            text = text.lower().strip()
            text = self.patterns['urls'].sub(' ', text)
            text = self.patterns['emails'].sub(' ', text)
            text = self.patterns['special_chars'].sub(' ', text)
            text = self.patterns['extra_spaces'].sub(' ', text)
            return text.strip()
        except Exception as e:
            raise TextCleaningError(f"Erro na limpeza do texto: {str(e)}")

    def _validate_nlp_result(self, result: Dict[str, Any]) -> bool:
        """Valida o resultado do processamento NLP"""
        return isinstance(result, dict) and "intent" in result

    def _determine_intent(self, result: Dict[str, Any], confidence: float) -> IntentType:
        """Determina a intenção com base no resultado e confiança"""
        if confidence < self.min_confidence:
            return IntentType.UNKNOWN
        try:
            return IntentType(result.get("intent", "unknown"))
        except ValueError:
            return IntentType.UNKNOWN

    def _process_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa e valida as entidades extraídas"""
        return [
            entity for entity in entities
            if isinstance(entity, dict) and "type" in entity and "value" in entity
        ]

    def _create_error_result(self, error_message: str) -> NLPResult:
        """Cria um resultado de erro padronizado"""
        return NLPResult(
            intent=IntentType.ERROR,
            entities=[],
            confidence=0.0,
            cleaned_text="",
            error=error_message
        )
