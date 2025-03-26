import logging
import os
import sys

class LoggingConfig:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def get_logger(name: str):
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, LoggingConfig.LOG_LEVEL))
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger

logger = LoggingConfig.get_logger(__name__)
def setup_file_handler(log_dir: str = "logs"):
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Add file handler for persistent logging
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    ))
    logger.addHandler(file_handler)

    # Add exception hook for uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

# Initialize file logging
setup_file_handler()