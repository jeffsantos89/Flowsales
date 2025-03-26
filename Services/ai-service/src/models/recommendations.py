from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, index=True)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="recommendations")
    description = Column(String(255), nullable=True)
    confidence_level = Column(Float, nullable=True)
    last_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
    status = Column(String(20), default="active")
    metadata = Column(String(1000), nullable=True)
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, user_id={self.user_id}, score={self.score:.2f})>"
    
    @property
    def is_fresh(self):
        if not self.last_updated:
            return False
        return (datetime.datetime.utcnow() - self.last_updated).days < 7
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "score": self.score,
            "confidence_level": self.confidence_level,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }