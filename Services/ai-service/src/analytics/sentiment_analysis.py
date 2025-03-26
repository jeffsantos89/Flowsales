from textblob import TextBlob
from typing import Dict, Union, Optional
import logging
from functools import lru_cache
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalysis:
    """
    Análise de sentimentos avançada baseada em NLP para classificar opiniões de usuários.
    Inclui tratamento de erros, cache, limpeza de texto e métricas detalhadas.
    """

    def __init__(self, 
                 positive_threshold: float = 0.1,
                 negative_threshold: float = -0.1,
                 language: str = 'pt'):
        self.positive_threshold = positive_threshold
        self.negative_threshold = negative_threshold
        self.language = language

    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove caracteres especiais e normaliza o texto."""
        if not text:
            return ""
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        # Remove caracteres especiais
        text = re.sub(r'[^\w\s]', '', text)
        # Normaliza espaços
        return ' '.join(text.split())

    @lru_cache(maxsize=1000)
    def _get_sentiment_score(self, text: str) -> float:
        """Calcula o score de sentimento com cache para performance."""
        try:
            return TextBlob(text).sentiment.polarity
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento: {str(e)}")
            return 0.0

    def analyze_text(self, text: str) -> Dict[str, Union[str, float, Optional[str]]]:
        """
        Analisa o sentimento do texto e retorna um dicionário com resultados detalhados.

        Args:
            text (str): Texto para análise

        Returns:
            Dict com sentimento, score e metadata
        """
        if not isinstance(text, str):
            raise ValueError("Input deve ser uma string")

        if not text.strip():
            return {
                "sentiment": "neutro",
                "score": 0.0,
                "confidence": 0.0,
                "text_length": 0,
                "language": self.language,
                "error": "Texto vazio"
            }

        try:
            cleaned_text = self._clean_text(text)
            sentiment_score = self._get_sentiment_score(cleaned_text)
            
            # Determina o sentimento baseado nos thresholds
            if sentiment_score > self.positive_threshold:
                sentiment = "positivo"
            elif sentiment_score < self.negative_threshold:
                sentiment = "negativo"
            else:
                sentiment = "neutro"

            # Calcula confiança básica baseada no tamanho do texto
            confidence = min(len(cleaned_text.split()) / 100, 1.0)

            return {
                "sentiment": sentiment,
                "score": round(sentiment_score, 3),
                "confidence": round(confidence, 2),
                "text_length": len(cleaned_text),
                "language": self.language,
                "error": None
            }

        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {str(e)}")
            return {
                "sentiment": "neutro",
                "score": 0.0,
                "confidence": 0.0,
                "text_length": len(text),
                "language": self.language,
                "error": str(e)
            }
