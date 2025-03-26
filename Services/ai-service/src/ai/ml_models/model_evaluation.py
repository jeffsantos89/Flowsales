from __future__ import annotations
import datetime
import numpy as np
from typing import Dict, Union, List, Optional, Any, TypeVar
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    f1_score, roc_auc_score, precision_score, recall_score,
    accuracy_score, confusion_matrix
)
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import warnings
from enum import Enum
import json
from pathlib import Path

# Configuração avançada do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('model_evaluation.log')
    ]
)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"

@dataclass(frozen=True)
class BaseMetrics(ABC):
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    model_name: str = field(default="unknown_model")
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v.tolist() if isinstance(v, np.ndarray) else v 
                for k, v in self.__dict__.items()}
    
    def save_metrics(self, filepath: Union[str, Path]) -> None:
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

@dataclass(frozen=True)
class RegressionMetrics(BaseMetrics):
    mse: float
    rmse: float
    mae: float
    r2: float
    explained_variance: float = field(default=0.0)
    sample_size: int = field(default=0)
    
    @property
    def summary(self) -> str:
        return f"""
        Regression Metrics Summary:
        MSE: {self.mse:.4f}
        RMSE: {self.rmse:.4f}
        MAE: {self.mae:.4f}
        R2: {self.r2:.4f}
        Explained Variance: {self.explained_variance:.4f}
        Sample Size: {self.sample_size}
        """

@dataclass(frozen=True)
class ClassificationMetrics(BaseMetrics):
    accuracy: float
    f1: float
    precision: float
    recall: float
    roc_auc: float
    confusion_matrix: np.ndarray
    specificity: float = field(default=0.0)
    sample_size: int = field(default=0)
    
    @property
    def summary(self) -> str:
        return f"""
        Classification Metrics Summary:
        Accuracy: {self.accuracy:.4f}
        F1 Score: {self.f1:.4f}
        Precision: {self.precision:.4f}
        Recall: {self.recall:.4f}
        ROC AUC: {self.roc_auc:.4f}
        Specificity: {self.specificity:.4f}
        Sample Size: {self.sample_size}
        """

class ModelEvaluation:
    """
    Classe avançada para avaliação de modelos de machine learning.
    Suporta métricas para regressão e classificação com validação robusta,
    tratamento de erros e recursos de logging.
    """
    
    def __init__(self, metric_type: MetricType):
        self.metric_type = metric_type
        self._validation_threshold = 1e-10
        
    @staticmethod
    def validate_inputs(y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """
        Valida os inputs com verificações extensivas.
        
        Args:
            y_true: Valores reais
            y_pred: Valores preditos
            
        Raises:
            ValueError: Se os inputs forem inválidos
            TypeError: Se os tipos dos inputs forem incorretos
        """
        if not isinstance(y_true, (np.ndarray, list)):
            raise TypeError("y_true deve ser numpy.ndarray ou list")
        if not isinstance(y_pred, (np.ndarray, list)):
            raise TypeError("y_pred deve ser numpy.ndarray ou list")
            
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        
        if len(y_true) != len(y_pred):
            raise ValueError("y_true e y_pred devem ter o mesmo tamanho")
        
        if len(y_true) == 0:
            raise ValueError("Os arrays não podem estar vazios")
            
        if np.isnan(y_true).any() or np.isnan(y_pred).any():
            raise ValueError("Os arrays não podem conter valores NaN")
            
        if np.isinf(y_true).any() or np.isinf(y_pred).any():
            raise ValueError("Os arrays não podem conter valores infinitos")

    @staticmethod
    def handle_warnings():
        warnings.filterwarnings('always', category=UserWarning)
        warnings.filterwarnings('ignore', category=FutureWarning)
        
    def preprocess_inputs(self, y_true: np.ndarray, y_pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Pré-processa os inputs para garantir formato correto.
        """
        y_true = np.asarray(y_true).reshape(-1)
        y_pred = np.asarray(y_pred).reshape(-1)
        return y_true, y_pred
