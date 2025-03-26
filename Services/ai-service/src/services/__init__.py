import logging
from services.data_processing import DataProcessor
from services.model_training import ModelTrainer
from services.prediction import Predictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        self.predictor = Predictor()
        logger.info("AIService initialized")

    def process_data(self, data):
        logger.info("Processing data")
        processed_data = self.data_processor.process(data)
        logger.info("Data processed successfully")
        return processed_data

    def train_model(self, training_data):
        logger.info("Training model")
        model = self.model_trainer.train(training_data)
        logger.info("Model trained successfully")
        return model

    def make_prediction(self, model, input_data):
        logger.info("Making prediction")
        prediction = self.predictor.predict(model, input_data)
        logger.info("Prediction made successfully")
        return prediction

# Initialize the AIService
ai_service = AIService()
logger.info("AIService module loaded")