import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import logging
from typing import Tuple, Optional
import json
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Model configuration parameters"""
    hidden_layers: list = None
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 50
    validation_split: float = 0.2
    early_stopping_patience: int = 5

class ModelOptimizer:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize optimizer with optional config file"""
        self.config = ModelConfig()
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
                for key, value in config_dict.items():
                    setattr(self.config, key, value)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise

    def optimize_model(self, model: tf.keras.Model) -> Tuple[bytes, dict]:
        """Optimize model for inference and return metrics"""
        try:
            logger.info("Starting model optimization")
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            
            # Enable optimization flags
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.float16]
            
            tflite_model = converter.convert()
            
            optimization_metrics = {
                "original_size": len(model.get_weights()),
                "optimized_size": len(tflite_model),
                "compression_ratio": len(model.get_weights()) / len(tflite_model)
            }
            
            logger.info(f"Model optimization complete: {optimization_metrics}")
            return tflite_model, optimization_metrics
            
        except Exception as e:
            logger.error(f"Error in model optimization: {str(e)}")
            raise

    def train_model(self, X: np.ndarray, y: np.ndarray) -> Tuple[tf.keras.Model, dict]:
        """Train model with optimal parameters and return metrics"""
        try:
            logger.info("Starting model training")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=self.config.validation_split, 
                random_state=42
            )

            model = self._build_model(input_shape=X_train.shape[1])
            
            # Add early stopping
            early_stopping = tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config.early_stopping_patience,
                restore_best_weights=True
            )

            history = model.fit(
                X_train, y_train,
                epochs=self.config.epochs,
                batch_size=self.config.batch_size,
                validation_data=(X_test, y_test),
                callbacks=[early_stopping]
            )

            metrics = self._evaluate_model(model, X_test, y_test, history)
            logger.info(f"Training complete: {metrics}")
            
            return model, metrics

        except Exception as e:
            logger.error(f"Error in model training: {str(e)}")
            raise

    def _build_model(self, input_shape: int) -> tf.keras.Model:
        """Build model architecture"""
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.InputLayer(input_shape=(input_shape,)))
        
        for units in self.config.hidden_layers or [128, 64]:
            model.add(tf.keras.layers.Dense(
                units, 
                activation='relu',
                kernel_regularizer=tf.keras.regularizers.l2(0.01)
            ))
            model.add(tf.keras.layers.BatchNormalization())
            model.add(tf.keras.layers.Dropout(0.2))
        
        model.add(tf.keras.layers.Dense(1))
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.config.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        return model

    def _evaluate_model(self, model: tf.keras.Model, X_test: np.ndarray, 
                       y_test: np.ndarray, history: dict) -> dict:
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        return {
            "mse": mean_squared_error(y_test, y_pred),
            "r2_score": r2_score(y_test, y_pred),
            "final_loss": float(history.history['loss'][-1]),
            "final_val_loss": float(history.history['val_loss'][-1])
        }

if __name__ == "__main__":
    logger.info("Model optimization system initialized")
