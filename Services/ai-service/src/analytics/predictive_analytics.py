import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import logging
from typing import Tuple, Any, Dict, Optional
import os

class PredictiveAnalytics:
    """
    Modelos avançados de análise preditiva para previsão de métricas de negócio.
    """

    def __init__(self, data: pd.DataFrame, target_column: str, model_path: str = "models"):
        """
        Inicializa o modelo de análise preditiva.
        
        Args:
            data: DataFrame com os dados de treino
            target_column: Nome da coluna alvo para previsão
            model_path: Caminho para salvar/carregar modelos
        """
        self.data = data
        self.target = target_column
        self.model_path = model_path
        self.pipeline = None
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configura o sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def preprocess_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara os dados para treinamento, lidando com valores ausentes e outliers.
        """
        try:
            # Tratamento de valores ausentes
            self.data = self.data.fillna(self.data.mean())
            
            # Separação de features e target
            X = self.data.drop(columns=[self.target])
            y = self.data[self.target]
            
            return X, y
        except Exception as e:
            self.logger.error(f"Erro no pré-processamento: {str(e)}")
            raise

    def create_pipeline(self, model_type: str = "rf") -> Pipeline:
        """
        Cria um pipeline de processamento e modelo.
        
        Args:
            model_type: Tipo de modelo ('rf' para Random Forest, 'gb' para Gradient Boosting)
        """
        if model_type == "rf":
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42
            )
        elif model_type == "gb":
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )

        return Pipeline([
            ('scaler', StandardScaler()),
            ('model', model)
        ])

    def train_model(self, model_type: str = "rf", cv_folds: int = 5) -> Dict[str, Any]:
        """
        Treina o modelo e avalia sua performance.
        
        Args:
            model_type: Tipo de modelo a ser usado
            cv_folds: Número de folds para validação cruzada
        """
        try:
            X, y = self.preprocess_data()
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            self.pipeline = self.create_pipeline(model_type)
            
            # Treinamento
            self.pipeline.fit(X_train, y_train)
            
            # Avaliação
            cv_scores = cross_val_score(self.pipeline, X_train, y_train, cv=cv_folds)
            y_pred = self.pipeline.predict(X_test)
            
            metrics = {
                'r2_score': r2_score(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            self.logger.info(f"Modelo treinado com métricas: {metrics}")
            self.save_model()
            
            return metrics

        except Exception as e:
            self.logger.error(f"Erro no treinamento: {str(e)}")
            raise

    def save_model(self) -> None:
        """Salva o modelo treinado em disco."""
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        
        model_file = os.path.join(self.model_path, 'model.joblib')
        joblib.dump(self.pipeline, model_file)
        self.logger.info(f"Modelo salvo em {model_file}")

    def load_model(self) -> None:
        """Carrega um modelo previamente treinado."""
        model_file = os.path.join(self.model_path, 'model.joblib')
        if os.path.exists(model_file):
            self.pipeline = joblib.load(model_file)
            self.logger.info("Modelo carregado com sucesso")
        else:
            raise FileNotFoundError("Modelo não encontrado")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Realiza previsões com o modelo treinado.
        
        Args:
            X: DataFrame com dados para previsão
        """
        if self.pipeline is None:
            self.load_model()
        
        try:
            predictions = self.pipeline.predict(X)
            return predictions
        except Exception as e:
            self.logger.error(f"Erro na previsão: {str(e)}")
            raise
