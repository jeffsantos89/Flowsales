import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error
from typing import Dict, Any

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluation:
    """Classe para avaliação de modelos de Machine Learning"""

    @staticmethod
    def classification_metrics(y_true: Any, y_pred: Any) -> Dict[str, float]:
        """
        Calcula métricas de avaliação para modelos de classificação.

        Args:
            y_true (Any): Valores reais.
            y_pred (Any): Valores previstos.

        Returns:
            Dict[str, float]: Dicionário contendo as métricas de avaliação.
        """
        try:
            metrics = {
                "accuracy": accuracy_score(y_true, y_pred),
                "precision": precision_score(y_true, y_pred, average="weighted"),
                "recall": recall_score(y_true, y_pred, average="weighted"),
                "f1_score": f1_score(y_true, y_pred, average="weighted"),
            }
            logger.info("Classificação métricas calculadas com sucesso.")
            return metrics
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de classificação: {e}")
            raise

    @staticmethod
    def regression_metrics(y_true: Any, y_pred: Any) -> Dict[str, float]:
        """
        Calcula métricas de avaliação para modelos de regressão.

        Args:
            y_true (Any): Valores reais.
            y_pred (Any): Valores previstos.

        Returns:
            Dict[str, float]: Dicionário contendo as métricas de avaliação.
        """
        try:
            metrics = {
                "mse": mean_squared_error(y_true, y_pred),
                "rmse": mean_squared_error(y_true, y_pred, squared=False),
            }
            logger.info("Regressão métricas calculadas com sucesso.")
            return metrics
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de regressão: {e}")
            raise

# Instância da classe ModelEvaluation
model_evaluation = ModelEvaluation()
