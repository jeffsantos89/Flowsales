import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore

class AnalyticsUtils:
    """
    Conjunto de funções auxiliares para análise de dados, manipulação e visualização.
    """

    @staticmethod
    def detect_outliers(data: pd.DataFrame, column: str, method="zscore"):
        """
        Detecta outliers em uma coluna específica usando Z-Score ou IQR.
        
        :param data: DataFrame contendo os dados
        :param column: Nome da coluna a ser analisada
        :param method: Método de detecção ('zscore' ou 'iqr')
        :return: DataFrame com uma coluna extra indicando os outliers
        """
        df = data.copy()
        
        if method == "zscore":
            df["outlier"] = np.abs(zscore(df[column])) > 3
        elif method == "iqr":
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            df["outlier"] = (df[column] < (Q1 - 1.5 * IQR)) | (df[column] > (Q3 + 1.5 * IQR))
        else:
            raise ValueError("Método inválido! Escolha 'zscore' ou 'iqr'.")
        
        return df

    @staticmethod
    def plot_correlation_matrix(data: pd.DataFrame):
        """
        Plota a matriz de correlação entre as variáveis do DataFrame.
        
        :param data: DataFrame contendo os dados
        """
        corr_matrix = data.corr()
        plt.figure(figsize=(10, 6))
        plt.imshow(corr_matrix, cmap="coolwarm", interpolation="nearest")
        plt.colorbar()
        plt.title("Matriz de Correlação")
        plt.show()

    @staticmethod
    def generate_summary_statistics(data: pd.DataFrame):
        """
        Gera estatísticas descritivas básicas para um DataFrame.
        
        :param data: DataFrame contendo os dados
        :return: DataFrame com estatísticas descritivas
        """
        return data.describe()

    @staticmethod
    def normalize_data(data: pd.DataFrame):
        """
        Normaliza os dados numéricos de um DataFrame.
        
        :param data: DataFrame contendo os dados
        :return: DataFrame normalizado
        """
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = (data[numeric_cols] - data[numeric_cols].min()) / (data[numeric_cols].max() - data[numeric_cols].min())
        return data

    @staticmethod
    def rolling_average(data: pd.Series, window_size=7):
        """
        Calcula a média móvel para suavizar tendências nos dados.
        
        :param data: Série temporal
        :param window_size: Tamanho da janela para a média móvel
        :return: Série temporal suavizada
        """
        return data.rolling(window=window_size).mean()
        @staticmethod
        def handle_missing_values(data: pd.DataFrame, strategy: str = 'mean', threshold: float = 0.5) -> pd.DataFrame:
            """
            Handles missing values in DataFrame with multiple strategies.
            
            :param data: Input DataFrame
            :param strategy: Strategy to handle missing values ('mean', 'median', 'mode', 'drop')
            :param threshold: Maximum ratio of missing values allowed before dropping column
            :return: Processed DataFrame
            """
            df = data.copy()
            
            # Drop columns with too many missing values
            missing_ratio = df.isnull().sum() / len(df)
            df = df.drop(columns=missing_ratio[missing_ratio > threshold].index)
            
            if strategy == 'drop':
                return df.dropna()
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(exclude=[np.number]).columns
            
            for col in numeric_cols:
                if strategy == 'mean':
                    df[col].fillna(df[col].mean(), inplace=True)
                elif strategy == 'median':
                    df[col].fillna(df[col].median(), inplace=True)
            
            for col in categorical_cols:
                df[col].fillna(df[col].mode()[0], inplace=True)
                
            return df

        @staticmethod
        def remove_duplicates(data: pd.DataFrame, subset: list = None, keep: str = 'first') -> pd.DataFrame:
            """
            Removes duplicate rows based on specified columns.
            
            :param data: Input DataFrame
            :param subset: List of columns to consider for duplicates
            :param keep: Which duplicate to keep ('first', 'last', False)
            :return: DataFrame without duplicates
            """
            return data.drop_duplicates(subset=subset, keep=keep)

        @staticmethod
        def validate_data_types(data: pd.DataFrame, schema: dict) -> bool:
            """
            Validates DataFrame columns against expected data types.
            
            :param data: Input DataFrame
            :param schema: Dictionary of column names and expected dtypes
            :return: Boolean indicating if validation passed
            """
            try:
                for column, dtype in schema.items():
                    if column not in data.columns:
                        raise ValueError(f"Column {column} not found in DataFrame")
                    if not np.issubdtype(data[column].dtype, dtype):
                        raise TypeError(f"Column {column} has incorrect dtype")
                return True
            except (ValueError, TypeError) as e:
                print(f"Validation error: {str(e)}")
                return False

        @staticmethod
        def feature_engineering(data: pd.DataFrame, date_column: str = None) -> pd.DataFrame:
            """
            Performs basic feature engineering on DataFrame.
            
            :param data: Input DataFrame
            :param date_column: Name of datetime column if time-based features needed
            :return: DataFrame with engineered features
            """
            df = data.copy()
            
            if date_column and date_column in df.columns:
                df[date_column] = pd.to_datetime(df[date_column])
                df[f'{date_column}_year'] = df[date_column].dt.year
                df[f'{date_column}_month'] = df[date_column].dt.month
                df[f'{date_column}_day'] = df[date_column].dt.day
                df[f'{date_column}_dayofweek'] = df[date_column].dt.dayofweek
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                df[f'{col}_squared'] = df[col] ** 2
                df[f'{col}_log'] = np.log1p(df[col].clip(lower=0))
                
            return df