import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import List, Dict, Optional
import logging
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path

class DataProcessing:
    """
    Pipeline avançado de processamento de dados para análise e machine learning.
    """

    def __init__(self, data: pd.DataFrame, model_path: str = "models"):
        """
        Inicializa o processador de dados.
        
        Args:
            data: DataFrame de entrada
            model_path: Caminho para salvar/carregar transformadores
        """
        self.data = data.copy()
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        self.transformers = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configura o sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _get_column_types(self) -> Dict[str, List[str]]:
        """Identifica e categoriza as colunas por tipo."""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.data.select_dtypes(include=["object"]).columns.tolist()
        return {
            "numeric": numeric_cols,
            "categorical": categorical_cols
        }

    def handle_missing_values(self, strategy: Dict[str, str] = None) -> None:
        """
        Trata valores ausentes usando diferentes estratégias.
        
        Args:
            strategy: Dicionário com estratégias por tipo de coluna
        """
        if strategy is None:
            strategy = {"numeric": "mean", "categorical": "most_frequent"}

        self.logger.info("Iniciando tratamento de valores ausentes...")
        
        for col_type, cols in self._get_column_types().items():
            if cols:
                imputer = SimpleImputer(strategy=strategy[col_type])
                self.data[cols] = imputer.fit_transform(self.data[cols])
                self.transformers[f"imputer_{col_type}"] = imputer

        self.logger.info("Tratamento de valores ausentes concluído")

    def normalize_numerical_features(self, method: str = "standard") -> None:
        """
        Normaliza features numéricas.
        
        Args:
            method: Método de normalização ('standard' ou 'minmax')
        """
        numeric_cols = self._get_column_types()["numeric"]
        if not numeric_cols:
            self.logger.warning("Nenhuma coluna numérica encontrada")
            return

        self.logger.info(f"Normalizando features numéricas usando método {method}")
        scaler = StandardScaler()
        self.data[numeric_cols] = scaler.fit_transform(self.data[numeric_cols])
        self.transformers["scaler"] = scaler

    def encode_categorical_features(self, encoding_method: str = "label") -> None:
        """
        Codifica features categóricas.
        
        Args:
            encoding_method: Método de codificação ('label' ou 'onehot')
        """
        categorical_cols = self._get_column_types()["categorical"]
        if not categorical_cols:
            self.logger.warning("Nenhuma coluna categórica encontrada")
            return

        self.logger.info(f"Codificando features categóricas usando {encoding_method}")
        
        if encoding_method == "label":
            for col in categorical_cols:
                encoder = LabelEncoder()
                self.data[col] = encoder.fit_transform(self.data[col])
                self.transformers[f"encoder_{col}"] = encoder
        elif encoding_method == "onehot":
            self.data = pd.get_dummies(self.data, columns=categorical_cols)

    def save_transformers(self) -> None:
        """Salva os transformadores para uso futuro."""
        for name, transformer in self.transformers.items():
            joblib.dump(transformer, self.model_path / f"{name}.joblib")
        self.logger.info("Transformadores salvos com sucesso")

    def load_transformers(self) -> None:
        """Carrega transformadores salvos."""
        for file in self.model_path.glob("*.joblib"):
            name = file.stem
            self.transformers[name] = joblib.load(file)
        self.logger.info("Transformadores carregados com sucesso")

    def preprocess_data(self, 
                       handle_missing: bool = True,
                       normalize: bool = True,
                       encode: bool = True,
                       save_state: bool = True) -> pd.DataFrame:
        """
        Executa o pipeline completo de pré-processamento.
        
        Args:
            handle_missing: Se deve tratar valores ausentes
            normalize: Se deve normalizar features numéricas
            encode: Se deve codificar features categóricas
            save_state: Se deve salvar os transformadores
        
        Returns:
            DataFrame processado
        """
        self.logger.info("Iniciando pipeline de pré-processamento")
        
        try:
            if handle_missing:
                self.handle_missing_values()
            if normalize:
                self.normalize_numerical_features()
            if encode:
                self.encode_categorical_features()
            if save_state:
                self.save_transformers()
                
            self.logger.info("Pré-processamento concluído com sucesso")
            return self.data
            
        except Exception as e:
            self.logger.error(f"Erro durante o pré-processamento: {str(e)}")
            raise

