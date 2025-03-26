from enum import Enum
from typing import Dict, List, Optional
import spacy
from dataclasses import dataclass
import logging
from collections import defaultdict

class IntentType(Enum):
    PRODUCT_INFO = "product_info"
    PRICE_COMPARISON = "price_comparison"
    RECOMMENDATIONS = "recommendations"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"

@dataclass
class IntentConfig:
    keywords: List[str]
    weight: float = 1.0
    required_words: List[str] = None
    excluded_words: List[str] = None

class NLPProcessor:
    def __init__(self, language_model: str = "pt_core_news_sm"):
        """
        Initialize NLP processor with spaCy model and intent configurations.
        
        Args:
            language_model: The spaCy language model to use
        """
        try:
            self.nlp = spacy.load(language_model)
        except OSError:
            logging.error(f"Failed to load language model: {language_model}")
            raise

        self._setup_intent_configs()
        self.logger = logging.getLogger(__name__)

    def _setup_intent_configs(self) -> None:
        """Configure intent detection rules and patterns."""
        self.intent_configs: Dict[IntentType, IntentConfig] = {
            IntentType.PRODUCT_INFO: IntentConfig(
                keywords=["detalhes", "informações", "características", "mostrar", "sobre", "especificações"],
                weight=1.2,
                required_words=["produto", "item"]
            ),
            IntentType.PRICE_COMPARISON: IntentConfig(
                keywords=["preço", "barato", "caro", "comparar", "custo", "valor", "quanto custa"],
                weight=1.5
            ),
            IntentType.RECOMMENDATIONS: IntentConfig(
                keywords=["recomendar", "sugestão", "indicação", "similar", "parecido", "alternativa"],
                weight=1.3
            )
        }

    def classify_intent(self, query: str) -> IntentType:
        """
        Classify the intent of a given query using NLP processing.
        
        Args:
            query: Input text to classify
            
        Returns:
            IntentType: Classified intent
        """
        try:
            if not query.strip():
                return IntentType.UNKNOWN

            doc = self.nlp(query.lower())
            scores = defaultdict(float)

            # Process tokens and calculate intent scores
            for token in doc:
                if not token.is_stop and not token.is_punct:
                    self._calculate_token_scores(token.text, scores)

            # Apply weights and requirements
            final_scores = self._apply_intent_rules(doc, scores)

            # Get the highest scoring intent
            if final_scores:
                max_intent = max(final_scores.items(), key=lambda x: x[1])[0]
                self.logger.info(f"Classified intent: {max_intent} for query: {query}")
                return max_intent

            return IntentType.GENERAL_QUERY

        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return IntentType.UNKNOWN

    def _calculate_token_scores(self, token: str, scores: Dict[IntentType, float]) -> None:
        """Calculate scores for each token against intent keywords."""
        for intent_type, config in self.intent_configs.items():
            if token in config.keywords:
                scores[intent_type] += config.weight

    def _apply_intent_rules(self, doc, scores: Dict[IntentType, float]) -> Dict[IntentType, float]:
        """Apply additional rules and requirements to intent scores."""
        final_scores = {}
        doc_text = doc.text.lower()

        for intent_type, config in self.intent_configs.items():
            if scores[intent_type] > 0:
                if config.required_words and not any(word in doc_text for word in config.required_words):
                    continue
                if config.excluded_words and any(word in doc_text for word in config.excluded_words):
                    continue
                final_scores[intent_type] = scores[intent_type]

        return final_scores

    def train(self, training_data: List[tuple]) -> None:
        """
        Train the model with new examples (placeholder for future implementation).
        
        Args:
            training_data: List of (text, intent) tuples
        """
        # TODO: Implement training logic
        pass
# chatbots/nlp_processor.py
class NLPProcessor:
    def classify_intent(self, text: str) -> str:
        text = text.lower()
        if any(keyword in text for keyword in ["comprar", "produto", "preço"]):
            return "sales"
        if any(keyword in text for keyword in ["suporte", "problema", "ajuda"]):
            return "support"
        return "general"
