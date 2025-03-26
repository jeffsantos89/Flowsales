import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from typing import Optional, Union, List, Dict
import logging
import joblib
from pathlib import Path

class AnomalyDetection:
    """
    Detecta padrões anômalos que podem indicar fraudes ou comportamentos incomuns.
    Implementa técnicas de pré-processamento, validação e persistência do modelo.
    """

    def __init__(self, 
                 nu: float = 0.1, 
                 kernel: str = "rbf", 
                 gamma: Union[str, float] = "auto",
                 random_state: int = 42):
        """
        Inicializa o detector de anomalias.

        Args:
            nu: Limite superior da fração de outliers (0 < nu < 1)
            kernel: Kernel do SVM ('rbf', 'linear', 'poly')
            gamma: Coeficiente do kernel
            random_state: Seed para reprodutibilidade
        """
        self.model = OneClassSVM(
            nu=nu,
            kernel=kernel,
            gamma=gamma,
            random_state=random_state
        )
        self.scaler = StandardScaler()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configura o logger para a classe."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _validate_data(self, data: np.ndarray) -> bool:
        """
        Valida os dados de entrada.
        
        Returns:
            bool: True se os dados são válidos
        """
        if data is None or len(data) == 0:
            self.logger.error("Dados vazios ou nulos")
            return False
        if np.isnan(data).any():
            self.logger.error("Dados contêm valores NaN")
            return False
        return True

    def fit(self, data: np.ndarray) -> 'AnomalyDetection':
        """
        Treina o modelo com os dados fornecidos.

        Args:
            data: Array numpy com features para treino

        Returns:
            self: Instância treinada do detector
        """
        if not self._validate_data(data):
            raise ValueError("Dados inválidos para treinamento")

        try:
            self.logger.info("Iniciando treinamento do modelo...")
            scaled_data = self.scaler.fit_transform(data)
            self.model.fit(scaled_data)
            self.logger.info("Modelo treinado com sucesso")
            return self
        except Exception as e:
            self.logger.error(f"Erro durante o treinamento: {str(e)}")
            raise

    def detect_anomalies(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Detecta anomalias nos dados fornecidos.

        Args:
            data: Array numpy com features para predição

        Returns:
            Dict com predictions (-1 para anomalias, 1 para normal) e scores
        """
        if not self._validate_data(data):
            raise ValueError("Dados inválidos para predição")

        try:
            scaled_data = self.scaler.transform(data)
            predictions = self.model.predict(scaled_data)
            scores = self.model.score_samples(scaled_data)
            
            return {
                "predictions": predictions,
                "anomaly_scores": scores
            }
        except Exception as e:
            self.logger.error(f"Erro durante a predição: {str(e)}")
            raise

    def save_model(self, path: str) -> None:
        """Salva o modelo treinado e o scaler em disco."""
        try:
            model_path = Path(path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler
            }, path)
            self.logger.info(f"Modelo salvo em {path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelo: {str(e)}")
            raise

    @classmethod
    def load_model(cls, path: str) -> 'AnomalyDetection':
        """Carrega um modelo salvo do disco."""
        try:
            components = joblib.load(path)
            instance = cls()
            instance.model = components['model']
            instance.scaler = components['scaler']
            instance.logger.info(f"Modelo carregado de {path}")
            return instance
        except Exception as e:
            logging.error(f"Erro ao carregar modelo: {str(e)}")
            raise
