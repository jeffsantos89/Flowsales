import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
import numpy as np
import joblib
import logging
import os

class FeatureEngineering:
    """ Classe para processamento e engenharia de features """

    def __init__(self, scaler_path='scaler.pkl', encoder_path='encoder.pkl'):
        self.scaler_path = scaler_path
        self.encoder_path = encoder_path
        self.scaler = self._load_model(scaler_path, StandardScaler())
        self.encoder = self._load_model(encoder_path, OneHotEncoder(handle_unknown="ignore"))
        logging.basicConfig(level=logging.INFO)

    def _load_model(self, path, default_model):
        if os.path.exists(path):
            logging.info(f"Loading model from {path}")
            return joblib.load(path)
        else:
            logging.info(f"No model found at {path}, using default model")
            return default_model

    def _save_model(self, model, path):
        joblib.dump(model, path)
        logging.info(f"Model saved to {path}")

    def transform_numeric(self, df: pd.DataFrame, columns: list):
        """ Escala variáveis numéricas """
        try:
            df[columns] = self.scaler.fit_transform(df[columns])
            self._save_model(self.scaler, self.scaler_path)
            return df
        except Exception as e:
            logging.error(f"Error in transform_numeric: {e}")
            raise

    def transform_categorical(self, df: pd.DataFrame, columns: list):
        """ Converte categorias para one-hot encoding """
        try:
            encoded = self.encoder.fit_transform(df[columns]).toarray()
            encoded_df = pd.DataFrame(encoded, columns=self.encoder.get_feature_names_out())
            self._save_model(self.encoder, self.encoder_path)
            return df.join(encoded_df).drop(columns, axis=1)
        except Exception as e:
            logging.error(f"Error in transform_categorical: {e}")
            raise

feature_engineering = FeatureEngineering()

