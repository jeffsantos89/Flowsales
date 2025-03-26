from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from ai.database import db_session
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

class Base(DeclarativeBase):
    pass
from fastapi import HTTPException
import logging
from functools import wraps

T = TypeVar('T', bound=Base)

def handle_db_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            logging.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.logger = logging.getLogger(__name__)

    @handle_db_exceptions
    async def get_by_id(self, db: Session, id: int) -> Optional[T]:
        """
        Busca um registro pelo ID.
        Raises:
            HTTPException: Se ocorrer erro no banco de dados
        """
        return db.query(self.model).filter(self.model.id == id).first()

    @handle_db_exceptions
    async def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Retorna registros com paginação.
        Args:
            skip: Quantidade de registros para pular
            limit: Limite de registros a retornar
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    @handle_db_exceptions
    async def create(self, db: Session, obj: T) -> T:
        """
        Insere um novo registro no banco.
        Validates:
            Verifica se objeto é válido antes de inserir
        """
        if not obj:
            raise HTTPException(status_code=400, detail="Invalid data provided")
        
        try:
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except SQLAlchemyError:
            db.rollback()
            raise

    @handle_db_exceptions
    async def update(self, db: Session, obj: T, updates: Dict[str, Any]) -> T:
        """
        Atualiza um registro existente.
        Validates:
            Verifica campos permitidos para atualização
        """
        if not obj:
            raise HTTPException(status_code=404, detail="Record not found")

        allowed_fields = [column.key for column in self.model.__table__.columns]
        invalid_fields = [key for key in updates.keys() if key not in allowed_fields]
        
        if invalid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid fields: {', '.join(invalid_fields)}"
            )

        try:
            for key, value in updates.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            return obj
        except SQLAlchemyError:
            db.rollback()
            raise

    @handle_db_exceptions
    async def delete(self, db: Session, id: int) -> Optional[T]:
        """
        Remove um registro do banco.
        Raises:
            HTTPException: Se registro não encontrado
        """
        obj = await self.get_by_id(db, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Record not found")
        
        try:
            db.delete(obj)
            db.commit()
            return obj
        except SQLAlchemyError:
            db.rollback()
            raise

    @handle_db_exceptions
    async def count(self, db: Session) -> int:
        """Retorna quantidade total de registros"""
        return db.query(self.model).count()

    @handle_db_exceptions
    async def exists(self, db: Session, id: int) -> bool:
        """Verifica se registro existe"""
        return db.query(self.model).filter(self.model.id == id).first() is not None

    async def bulk_create(self, db: Session, objects: List[T]) -> List[T]:
        """Insere múltiplos registros em batch"""
        try:
            db.bulk_save_objects(objects)
            db.commit()
            return objects
        except SQLAlchemyError:
            db.rollback()
            raise

    async def execute_raw_query(self, db: Session, query: str, params: Dict = None) -> Any:
        """Executa query SQL raw com proteção contra injeção"""
        try:
            result = db.execute(text(query), params or {})
            return result
        except SQLAlchemyError:
            db.rollback()
            raise
