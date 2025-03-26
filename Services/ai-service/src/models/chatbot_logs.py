
# filepath: src/models/chatbot_logs.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ChatbotLog(Base):
    __tablename__ = "chatbot_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    input_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    intent = Column(String)
    confidence = Column(Float)
    error = Column(Boolean, default=False)
    error_message = Column(Text)

    def __repr__(self):
        return f"<ChatbotLog(user_id='{self.user_id}', input_text='{self.input_text}', response_text='{self.response_text}')>"