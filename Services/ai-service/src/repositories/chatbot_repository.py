from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

Base = declarative_base()

class ChatbotLog(Base):
    __tablename__ = "chatbot_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    message = Column(Text)
    response = Column(Text)
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)
from repositories.base_repository import BaseRepository

class ChatbotRepository(BaseRepository[ChatbotLog]):
    def __init__(self):
        super().__init__(ChatbotLog)

    def get_logs_by_platform(self, db: Session, platform: str, limit: int = 20):
        """ Retorna interações do chatbot por plataforma (WhatsApp, Messenger, Telegram, etc.). """
        return db.query(ChatbotLog).filter(ChatbotLog.platform == platform).order_by(ChatbotLog.timestamp.desc()).limit(limit).all()
        def get_logs_by_date_range(self, db: Session, start_date: str, end_date: str, platform: str = None):
            """Retorna interações do chatbot por período e opcionalmente por plataforma."""
            query = db.query(ChatbotLog).filter(
                ChatbotLog.timestamp.between(start_date, end_date)
            )
            if platform:
                query = query.filter(ChatbotLog.platform == platform)
            return query.order_by(ChatbotLog.timestamp.desc()).all()

        def get_logs_by_user(self, db: Session, user_id: str, limit: int = 20):
            """Retorna interações do chatbot por usuário específico."""
            return db.query(ChatbotLog).filter(
                ChatbotLog.user_id == user_id
            ).order_by(ChatbotLog.timestamp.desc()).limit(limit).all()

        def get_logs_with_error(self, db: Session, limit: int = 20):
            """Retorna interações que resultaram em erro."""
            return db.query(ChatbotLog).filter(
                ChatbotLog.error.isnot(None)
            ).order_by(ChatbotLog.timestamp.desc()).limit(limit).all()