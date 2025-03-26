from typing import Generator
from contextlib import contextmanager
import os
from functools import lru_cache

from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class DatabaseConfig:
    DATABASE_URL = os.getenv("DATABASE_URL")
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
    MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

Base = declarative_base()

class Database:
    def __init__(self):
        self._engine = None
        self._session_factory = None

    @lru_cache(maxsize=None)
    def get_engine(self):
        if not self._engine:
            if not DatabaseConfig.DATABASE_URL:
                raise ValueError("DATABASE_URL não configurada!")
            
            self._engine = create_engine(
                DatabaseConfig.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=DatabaseConfig.POOL_SIZE,
                max_overflow=DatabaseConfig.MAX_OVERFLOW,
                pool_timeout=DatabaseConfig.POOL_TIMEOUT,
                pool_recycle=DatabaseConfig.POOL_RECYCLE,
                echo=DatabaseConfig.ECHO,
                pool_pre_ping=True,  # Verifica conexões antes de usar
            )
        return self._engine

    def get_session_factory(self):
        if not self._session_factory:
            self._session_factory = sessionmaker(
                bind=self.get_engine(),
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        return self._session_factory

    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        session_factory = self.get_session_factory()
        session = session_factory()
        
        try:
            yield session
            session.commit()
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Database error: {str(e)}")
        finally:
            session.close()

# Instância global do banco de dados
db = Database()

# Função auxiliar para obter sessão
def get_db() -> Generator[Session, None, None]:
    with db.get_db_session() as session:
        yield session