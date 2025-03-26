import numpy as np
from ai.ml_models.predict import load_model, preprocess_data

model = load_model()

def predict_sales(input_data):
    processed_data = preprocess_data(input_data)
    return model.predict(np.array([processed_data]))[0]
    class PredictionService:
        def __init__(self):
            self.model = None
            self.initialize_model()

        def initialize_model(self):
            try:
                self.model = load_model()
            except Exception as e:
                raise RuntimeError(f"Failed to load model: {str(e)}")

        def predict_sales(self, input_data: dict) -> float:
            """
            Predicts sales based on input data.
            
            Args:
                input_data (dict): Input features for prediction
                
            Returns:
                float: Predicted sales value
                
            Raises:
                ValueError: If input data is invalid
                RuntimeError: If prediction fails
            """
            try:
                if not input_data:
                    raise ValueError("Input data cannot be empty")
                    
                processed_data = preprocess_data(input_data)
                prediction = self.model.predict(np.array([processed_data]))[0]
                
                return float(prediction)
                
            except Exception as e:
                raise RuntimeError(f"Prediction failed: {str(e)}")

    prediction_service = PredictionService()