from typing import List, Optional, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from logging import getLogger
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = getLogger(__name__)

@dataclass
class RecommendationResult:
    """Estrutura de dados para armazenar resultados da recomendação"""
    user_id: int
    recommended_users: pd.DataFrame
    similarity_scores: np.ndarray
    timestamp: pd.Timestamp

class SimilarityStrategy(ABC):
    """Interface para diferentes estratégias de similaridade"""
    @abstractmethod
    def calculate_similarity(self, data: pd.DataFrame) -> np.ndarray:
        pass

class CosineSimilarityStrategy(SimilarityStrategy):
    def calculate_similarity(self, data: pd.DataFrame) -> np.ndarray:
        return cosine_similarity(data)

class RecommendationEngine:
    """
    Sistema de recomendação baseado em similaridade de clientes.
    
    Attributes:
        user_profiles (pd.DataFrame): DataFrame contendo perfis dos usuários
        similarity_strategy (SimilarityStrategy): Estratégia para cálculo de similaridade
        cache (Dict): Cache para armazenar recomendações recentes
        max_recommendations (int): Número máximo de recomendações
    """

    def __init__(
        self, 
        user_profiles: pd.DataFrame,
        similarity_strategy: Optional[SimilarityStrategy] = None,
        max_recommendations: int = 5,
        cache_size: int = 1000
    ):
        self._validate_input(user_profiles)
        self.user_profiles = user_profiles
        self.similarity_strategy = similarity_strategy or CosineSimilarityStrategy()
        self.max_recommendations = max_recommendations
        self.cache = {}
        self.cache_size = cache_size

    def _validate_input(self, user_profiles: pd.DataFrame) -> None:
        """Valida os dados de entrada"""
        if user_profiles.empty:
            raise ValueError("User profiles DataFrame cannot be empty")
        if user_profiles.isnull().any().any():
            raise ValueError("User profiles contain null values")

    def _calculate_similarities(self) -> np.ndarray:
        """Calcula matriz de similaridade"""
        try:
            return self.similarity_strategy.calculate_similarity(self.user_profiles)
        except Exception as e:
            logger.error(f"Error calculating similarities: {str(e)}")
            raise

    def recommend(self, user_id: int, use_cache: bool = True) -> RecommendationResult:
        """
        Gera recomendações para um usuário específico.

        Args:
            user_id: ID do usuário
            use_cache: Se deve usar cache de recomendações

        Returns:
            RecommendationResult: Objeto contendo as recomendações
        """
        try:
            if use_cache and user_id in self.cache:
                return self.cache[user_id]

            if user_id not in self.user_profiles.index:
                raise ValueError(f"User ID {user_id} not found")

            similarities = self._calculate_similarities()
            similar_users_idx = similarities[user_id].argsort()[::-1][1:self.max_recommendations + 1]
            similar_users = self.user_profiles.iloc[similar_users_idx]
            similarity_scores = similarities[user_id][similar_users_idx]

            result = RecommendationResult(
                user_id=user_id,
                recommended_users=similar_users,
                similarity_scores=similarity_scores,
                timestamp=pd.Timestamp.now()
            )

            self._update_cache(user_id, result)
            return result

        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
            raise

    def _update_cache(self, user_id: int, result: RecommendationResult) -> None:
        """Atualiza o cache de recomendações"""
        if len(self.cache) >= self.cache_size:
            # Remove o item mais antigo do cache
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
            self.cache.pop(oldest_key)
        self.cache[user_id] = result

    def update_user_profiles(self, new_profiles: pd.DataFrame) -> None:
        """Atualiza os perfis de usuário e limpa o cache"""
        self._validate_input(new_profiles)
        self.user_profiles = new_profiles
        self.cache.clear()
