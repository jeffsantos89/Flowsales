# src/ai/ml_models/predict.py
import tensorflow as tf
import numpy as np
import logging
from typing import List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SalesPredictor:
    def __init__(self, model_path: str):
        self.model = self._load_model(model_path)

    def _load_model(self, model_path: str) -> tf.keras.Model:
        try:
            model = tf.keras.models.load_model(model_path)
            logging.info(f"Modelo carregado com sucesso de {model_path}")
            return model
        except Exception as e:
            logging.error(f"Erro ao carregar o modelo: {e}")
            raise

    def predict_sales(self, data: List[float]) -> List[float]:
        try:
            if not self._validate_input(data):
                raise ValueError("Dados de entrada inválidos")
            prediction = self.model.predict(np.array([data]))
            logging.info("Previsão realizada com sucesso")
            return prediction[0].tolist()
        except Exception as e:
            logging.error(f"Erro ao realizar a previsão: {e}")
            raise

    def _validate_input(self, data: List[float]) -> bool:
        # Adicione aqui validações específicas para os dados de entrada
        if not data or not isinstance(data, list):
            logging.error("Dados de entrada devem ser uma lista não vazia")
            return False
        if not all(isinstance(x, (int, float)) for x in data):
            logging.error("Todos os elementos dos dados de entrada devem ser números")
            return False
        return True

# Exemplo de uso
if __name__ == "__main__":
    model_path = "src/ai/ml_models/sales_forecast.h5"
    predictor = SalesPredictor(model_path)
    sample_data = [1.0, 2.0, 3.0]  # Substitua pelos seus dados reais
    try:
        prediction = predictor.predict_sales(sample_data)
        print(f"Previsão: {prediction}")
    except Exception as e:
        print(f"Erro: {e}")
