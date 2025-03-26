import logging
import os
from pathlib import Path
from typing import Tuple, Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.exceptions import NotFittedError
import yaml

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Classe responsável pelo treinamento e avaliação do modelo."""

    def __init__(self, config_path: str = 'config/model_config.yaml'):
        """
        Inicializa o treinador do modelo.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config = self._load_config(config_path)
        self.model = None
        self.metrics = {}

    def _load_config(self, config_path: str) -> dict:
        """Carrega configurações do modelo a partir de um arquivo YAML."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            raise

    def _prepare_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepara os dados para treinamento."""
        try:
            data_path = Path(self.config['data_path'])
            if not data_path.exists():
                raise FileNotFoundError(f"Arquivo de dados não encontrado: {data_path}")

            data = pd.read_csv(data_path)
            
            # Validação básica dos dados
            if data.isnull().any().any():
                logger.warning("Dados contêm valores nulos")
                data = data.dropna()

            X = data.iloc[:, :-1]
            y = data.iloc[:, -1]

            return train_test_split(
                X, y,
                test_size=self.config['test_size'],
                random_state=self.config['random_state']
            )

        except Exception as e:
            logger.error(f"Erro na preparação dos dados: {str(e)}")
            raise

    def train(self) -> None:
        """Treina o modelo com os parâmetros configurados."""
        try:
            logger.info("Iniciando treinamento do modelo...")
            X_train, X_test, y_train, y_test = self._prepare_data()

            self.model = RandomForestClassifier(
                n_estimators=self.config['model_params']['n_estimators'],
                max_depth=self.config['model_params']['max_depth'],
                random_state=self.config['random_state']
            )

            # Treinamento e avaliação
            self.model.fit(X_train, y_train)
            
            # Avaliação do modelo
            self._evaluate_model(X_test, y_test)
            
            # Salvando o modelo
            self._save_model()

            logger.info("Treinamento concluído com sucesso!")

        except Exception as e:
            logger.error(f"Erro durante o treinamento: {str(e)}")
            raise

    def _evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> None:
        """Avalia o modelo e armazena as métricas."""
        try:
            y_pred = self.model.predict(X_test)
            
            self.metrics = {
                'classification_report': classification_report(y_test, y_pred),
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'cross_val_scores': cross_val_score(
                    self.model, X_test, y_test, cv=5
                ).mean()
            }

            logger.info(f"Métricas de avaliação:\n{self.metrics['classification_report']}")

        except Exception as e:
            logger.error(f"Erro na avaliação do modelo: {str(e)}")
            raise

    def _save_model(self) -> None:
        """Salva o modelo treinado e suas métricas."""
        try:
            if not self.model:
                raise NotFittedError("Modelo ainda não foi treinado")

            # Criar diretório se não existir
            model_dir = Path(self.config['model_output_path']).parent
            model_dir.mkdir(parents=True, exist_ok=True)

            # Salvar modelo
            joblib.dump(self.model, self.config['model_output_path'])
            
            # Salvar métricas
            metrics_path = model_dir / 'model_metrics.yaml'
            with open(metrics_path, 'w') as f:
                yaml.dump(self.metrics, f)

            logger.info(f"Modelo salvo em: {self.config['model_output_path']}")

        except Exception as e:
            logger.error(f"Erro ao salvar o modelo: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        trainer = ModelTrainer()
        trainer.train()
    except Exception as e:
        logger.error(f"Erro na execução: {str(e)}")
        raise
