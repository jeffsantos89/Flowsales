import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import NotFittedError
import logging
from typing import Optional, Dict, Any
import pandas as pd

class CustomerSegmentation:
    """
    Implementa segmentação avançada de clientes usando K-means com recursos de
    pré-processamento, validação e logging.
    """

    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        """
        Inicializa o segmentador de clientes.

        Args:
            n_clusters: Número de segmentos desejados
            random_state: Seed para reprodutibilidade
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state)
        self.scaler = StandardScaler()
        self._is_fitted = False
        
        # Configuração de logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _validate_data(self, data: pd.DataFrame) -> None:
        """Valida os dados de entrada."""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("DataFrame is empty")
        if data.isnull().any().any():
            raise ValueError("DataFrame contains null values")

    def fit(self, data: pd.DataFrame) -> 'CustomerSegmentation':
        """
        Treina o modelo de segmentação.

        Args:
            data: DataFrame com features dos clientes

        Returns:
            self: Instância treinada do segmentador
        """
        try:
            self._validate_data(data)
            
            self.logger.info("Iniciando processo de segmentação com %d clusters", self.n_clusters)
            
            # Normalizando os dados
            scaled_data = self.scaler.fit_transform(data)
            
            # Treinando o modelo
            self.model.fit(scaled_data)
            
            self._is_fitted = True
            
            # Calculando métricas de qualidade
            self.inertia_ = self.model.inertia_
            self.cluster_centers_ = self.model.cluster_centers_
            
            self.logger.info("Segmentação concluída com sucesso. Inertia: %.2f", self.inertia_)
            
            return self
            
        except Exception as e:
            self.logger.error("Erro durante o treinamento: %s", str(e))
            raise

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prediz os segmentos para novos dados.

        Args:
            data: DataFrame com features dos clientes

        Returns:
            np.ndarray: Array com os segmentos preditos
        """
        if not self._is_fitted:
            raise NotFittedError("O modelo precisa ser treinado antes de fazer predições")
            
        self._validate_data(data)
        scaled_data = self.scaler.transform(data)
        return self.model.predict(scaled_data)

    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre os clusters.

        Returns:
            Dict com informações sobre os clusters
        """
        if not self._is_fitted:
            raise NotFittedError("O modelo precisa ser treinado primeiro")
            
        return {
            "n_clusters": self.n_clusters,
            "inertia": self.inertia_,
            "cluster_centers": self.cluster_centers_,
            "cluster_sizes": np.bincount(self.model.labels_)
        }

    def segment_customers(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Segmenta os clientes e retorna o DataFrame original com as segments.

        Args:
            data: DataFrame com features dos clientes

        Returns:
            DataFrame com nova coluna 'segment'
        """
        try:
            if not self._is_fitted:
                self.fit(data)
            
            segments = self.predict(data)
            result = data.copy()
            result['segment'] = segments
            
            self.logger.info("Segmentação aplicada com sucesso em %d clientes", len(data))
            
            return result
            
        except Exception as e:
            self.logger.error("Erro durante a segmentação: %s", str(e))
            raise
