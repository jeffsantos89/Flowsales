import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class LogLevel(Enum):
    """Níveis de log disponíveis"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

@dataclass
class LogConfig:
    """Configurações do logger"""
    name: Optional[str] = None
    log_file: str = "logs/event.log"
    log_level: LogLevel = LogLevel.INFO
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

class Logger:
    """Classe responsável pelo gerenciamento de logs"""
    _instance = None
    _loggers = {}

    def __new__(cls):
        """Implementação Singleton para garantir uma única instância"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_logger(cls, config: LogConfig = LogConfig()) -> logging.Logger:
        """
        Obtém ou cria um logger baseado na configuração fornecida
        
        Args:
            config: Configurações do logger
            
        Returns:
            logging.Logger: Logger configurado
        """
        if config.name in cls._loggers:
            return cls._loggers[config.name]

        logger = cls._setup_logger(config)
        cls._loggers[config.name] = logger
        return logger

    @staticmethod
    def _setup_logger(config: LogConfig) -> logging.Logger:
        """Configura um novo logger com as configurações especificadas"""
        # Criar diretório de logs se não existir
        log_path = Path(config.log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(config.name)
        logger.setLevel(config.log_level.value)
        logger.propagate = False

        formatter = logging.Formatter(
            config.format_string,
            datefmt=config.date_format
        )

        # Configurar handlers apenas se não existirem
        if not logger.handlers:
            # File Handler com rotação
            file_handler = RotatingFileHandler(
                config.log_file,
                maxBytes=config.max_bytes,
                backupCount=config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(config.log_level.value)

            # Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(config.log_level.value)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    @staticmethod
    def log_event(logger: logging.Logger, message: str, **kwargs):
        """Registra um evento com contexto adicional"""
        logger.info(f"[EVENT] {message}", extra=kwargs)

    @staticmethod
    def log_error(logger: logging.Logger, error: Exception, **kwargs):
        """Registra um erro com stack trace e contexto adicional"""
        logger.error(f"[ERROR] {str(error)}", exc_info=True, extra=kwargs)

    @staticmethod
    def log_warning(logger: logging.Logger, message: str, **kwargs):
        """Registra um aviso com contexto adicional"""
        logger.warning(f"[WARNING] {message}", extra=kwargs)

# Exemplo de uso
if __name__ == "__main__":
    # Criar configuração personalizada
    config = LogConfig(
        name="app_logger",
        log_file="logs/app.log",
        log_level=LogLevel.DEBUG
    )
    
    # Obter logger
    logger = Logger.get_logger(config)
    
    # Exemplo de logs
    Logger.log_event(logger, "Aplicação iniciada", user="admin")
    try:
        raise ValueError("Exemplo de erro")
    except Exception as e:
        Logger.log_error(logger, e, operation="exemplo")
    Logger.log_warning(logger, "Recurso deprecado", component="legacy_module")
