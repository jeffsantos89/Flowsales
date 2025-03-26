import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder, RobustScaler
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List, Optional, Dict, Any
import logging
import joblib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineering(BaseEstimator, TransformerMixin):
    """
    Classe avançada para engenharia de características com recursos de
    persistência, validação e tratamento de dados ausentes.
    """

    def __init__(
        self,
        numeric_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        scaler_type: str = "standard",
        handle_missing: bool = True,
        max_categories: int = 20
    ):
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.scaler_type = scaler_type
        self.handle_missing = handle_missing
        self.max_categories = max_categories
        self.scalers: Dict[str, Any] = {}
        self.encoders: Dict[str, Any] = {}
        self._is_fitted = False

    def _validate_input(self, data: pd.DataFrame) -> None:
        """Valida os dados de entrada."""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Os dados devem ser um pandas DataFrame")
        if data.empty:
            raise ValueError("O DataFrame está vazio")

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Trata valores ausentes nos dados."""
        if not self.handle_missing:
            return data

        logger.info("Tratando valores ausentes...")
        # Preenche numéricos com mediana
        numeric_data = data.select_dtypes(include=["float64", "int64"])
        data[numeric_data.columns] = data[numeric_data.columns].fillna(data[numeric_data.columns].median())
        
        # Preenche categóricos com moda
        categorical_data = data.select_dtypes(include=["object"])
        data[categorical_data.columns] = data[categorical_data.columns].fillna(data[categorical_data.columns].mode().iloc[0])
        
        return data

    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Normaliza características numéricas usando o scaler especificado."""
        if not self.numeric_features:
            self.numeric_features = data.select_dtypes(include=["float64", "int64"]).columns.tolist()

        if not self.numeric_features:
            return data

        logger.info("Normalizando características numéricas...")
        for feature in self.numeric_features:
            if feature not in data.columns:
                continue

            if self.scaler_type == "robust":
                self.scalers[feature] = RobustScaler()
            else:
                self.scalers[feature] = StandardScaler()

            data[feature] = self.scalers[feature].fit_transform(data[[feature]])

        return data

    def _encode_categorical(self, data: pd.DataFrame) -> pd.DataFrame:
        """Aplica OneHotEncoding em variáveis categóricas com controle de cardinalidade."""
        if not self.categorical_features:
            self.categorical_features = data.select_dtypes(include=["object"]).columns.tolist()

        if not self.categorical_features:
            return data

        logger.info("Codificando características categóricas...")
        for feature in self.categorical_features:
            if feature not in data.columns:
                continue

            # Limita o número de categorias para evitar explosão dimensional
            value_counts = data[feature].value_counts()
            if len(value_counts) > self.max_categories:
                top_categories = value_counts.nlargest(self.max_categories).index
                data[feature] = data[feature].apply(lambda x: x if x in top_categories else 'Other')

            encoder = OneHotEncoder(sparse_output=False, drop="first", handle_unknown="ignore")
            encoded = encoder.fit_transform(data[[feature]])
            feature_names = [f"{feature}_{cat}" for cat in encoder.get_feature_names_out([feature])]
            
            encoded_df = pd.DataFrame(encoded, columns=feature_names, index=data.index)
            data = pd.concat([data.drop(columns=[feature]), encoded_df], axis=1)
            self.encoders[feature] = encoder

        return data

    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Ajusta e transforma os dados."""
        self._validate_input(data)
        data = data.copy()
        data = self._handle_missing_values(data)
        data = self._normalize_features(data)
        data = self._encode_categorical(data)
        self._is_fitted = True
        return data

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transforma novos dados usando os parâmetros já ajustados."""
        if not self._is_fitted:
            raise ValueError("O modelo precisa ser ajustado primeiro usando fit_transform")
        
        self._validate_input(data)
        data = data.copy()
        data = self._handle_missing_values(data)
        
        # Aplica transformações usando os parâmetros ajustados
        for feature, scaler in self.scalers.items():
            if feature in data.columns:
                data[feature] = scaler.transform(data[[feature]])

        for feature, encoder in self.encoders.items():
            if feature in data.columns:
                encoded = encoder.transform(data[[feature]])
                feature_names = [f"{feature}_{cat}" for cat in encoder.get_feature_names_out([feature])]
                encoded_df = pd.DataFrame(encoded, columns=feature_names, index=data.index)
                data = pd.concat([data.drop(columns=[feature]), encoded_df], axis=1)

        return data

    def save_model(self, path: str) -> None:
        """Salva o modelo treinado."""
        if not self._is_fitted:
            raise ValueError("O modelo precisa ser ajustado antes de ser salvo")
        
        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, model_path)
        logger.info(f"Modelo salvo em {path}")

    @staticmethod
    def load_model(path: str) -> 'FeatureEngineering':
        """Carrega um modelo salvo."""
        model_path = Path(path)
        if not model_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        
        model = joblib.load(model_path)
        logger.info(f"Modelo carregado de {path}")
        return model
