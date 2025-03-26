import logging
import os
from datetime import datetime, timezone
from typing import List, Optional
from logging.config import dictConfig
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from database import Base
import re
from email_validator import validate_email, EmailNotValidError

class Logger:
    def __init__(self, service_name: str = "ai-service"):
        self.logger = logging.getLogger(service_name)
        self.configure_logger()

    def configure_logger(self) -> None:
        sentry_env = os.getenv("SENTRY_ENVIRONMENT", "development")
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN", ""),
            environment=sentry_env,
            traces_sample_rate=1.0,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
            ]
        )

        LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "localhost")
        LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", "5044"))

        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
            },
            'handlers': {
                'console': {
                    'level': os.getenv('LOG_LEVEL', 'INFO'),
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                },
                'logstash': {
                    'level': 'INFO',
                    'class': 'logstash_async.handler.AsynchronousLogstashHandler',
                    'host': LOGSTASH_HOST,
                    'port': LOGSTASH_PORT,
                    'database_path': None,
                    'transport': 'logstash_async.transport.TcpTransport'
                }
            },
            'loggers': {
                'ai-service': {
                    'handlers': ['console', 'logstash'],
                    'level': os.getenv('LOG_LEVEL', 'INFO'),
                    'propagate': False
                }
            }
        }

        try:
            dictConfig(log_config)
        except Exception as e:
            self.logger.error(f"Erro na configuração do logger: {str(e)}")
            log_config['loggers']['ai-service']['handlers'] = ['console']
            dictConfig(log_config)

    def info(self, message: str, extra: dict = None) -> None:
        self.logger.info(message, extra=extra)

    def error(self, message: str, exc_info: bool = True, extra: dict = None) -> None:
        self.logger.error(message, exc_info=exc_info, extra=extra)

    def warning(self, message: str, extra: dict = None) -> None:
        self.logger.warning(message, extra=extra)

    def debug(self, message: str, extra: dict = None) -> None:
        self.logger.debug(message, extra=extra)

logger = Logger()

class User(Base):
    """
    Modelo de usuário com validações e funcionalidades avançadas.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

    @validates('email')
    def validate_email(self, key: str, email: str) -> str:
        try:
            email_info = validate_email(email, check_deliverability=False)
            return email_info.normalized
        except EmailNotValidError as e:
            logger.error(f"Email inválido: {email}", extra={'error': str(e)})
            raise ValueError(f"Email inválido: {str(e)}")

    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        if not name or len(name.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        if not re.match("^[a-zA-Z0-9 ]+$", name):
            raise ValueError("Nome deve conter apenas letras, números e espaços")
        return name.strip()

    @hybrid_property
    def is_registered(self) -> bool:
        return bool(self.created_at)

    def update_last_login(self) -> None:
        self.last_login = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
