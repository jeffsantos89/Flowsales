import joblib
import tensorflow as tf
from flask import Flask, request, jsonify
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
import yaml
import numpy as np
from typing import Dict, Any, List
from werkzeug.exceptions import BadRequest

# Configuration
class Config:
    def __init__(self):
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        self.MODEL_PATH = self.config["model_paths"]
        self.LOG_PATH = self.config["log_path"]
        self.DEBUG = self.config["debug"]
        self.HOST = self.config["host"]
        self.PORT = self.config["port"]

# Error handling
class ModelError(Exception):
    pass

# Initialize Flask app
app = Flask(__name__)
config = Config()

# Setup logging
def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    file_handler = RotatingFileHandler(
        config.LOG_PATH,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# Model loading with error handling
class ModelManager:
    def __init__(self):
        self.ml_model = None
        self.quantum_model = None
        self.load_models()

    def load_models(self):
        try:
            self.ml_model = joblib.load(config.MODEL_PATH["ml"])
            self.quantum_model = tf.keras.models.load_model(
                config.MODEL_PATH["quantum"]
            )
        except Exception as e:
            app.logger.error(f"Failed to load models: {str(e)}")
            raise ModelError("Model loading failed")

# Request validation decorator
def validate_input(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.json or "input" not in request.json:
            raise BadRequest("Missing input data")
        
        input_data = request.json.get("input")
        if not isinstance(input_data, (list, np.ndarray)):
            raise BadRequest("Input must be a list or array")
            
        return f(*args, **kwargs)
    return decorated_function

# Initialize models
model_manager = ModelManager()

@app.route("/health", methods=["GET"])
def health_check() -> Dict[str, str]:
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/predict", methods=["POST"])
@validate_input
def predict() -> Dict[str, List]:
    try:
        data = request.json.get("input")
        prediction = model_manager.ml_model.predict([data])
        app.logger.info(f"Prediction made with ML model: {prediction}")
        return jsonify({"prediction": prediction.tolist()})
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/quantum_infer", methods=["POST"])
@validate_input
def quantum_infer() -> Dict[str, List]:
    try:
        data = request.json.get("input")
        prediction = model_manager.quantum_model.predict([data])
        app.logger.info(f"Prediction made with Quantum model: {prediction}")
        return jsonify({"quantum_prediction": prediction.tolist()})
    except Exception as e:
        app.logger.error(f"Quantum inference error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    setup_logging()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
