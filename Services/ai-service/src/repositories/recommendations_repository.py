from sqlalchemy.orm import Session
from models.recommendations import Recommendation
from repositories.base_repository import BaseRepository
from datetime import datetime, timedelta
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

class RecommendationsRepository(BaseRepository[Recommendation]):
    def __init__(self):
        super().__init__(Recommendation)

    def get_recommendations_by_user(self, db: Session, user_id: int):
        """ Busca recomendações personalizadas para um usuário. """
        return db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
        def create_recommendation(self, db: Session, user_id: int, product_id: int, score: float, recommendation_type: str) -> Recommendation:
            """Creates a new recommendation with error handling and validation."""
            try:
                recommendation = Recommendation(
                    user_id=user_id,
                    product_id=product_id,
                    score=min(max(score, 0.0), 1.0),  # Normalize score between 0 and 1
                    recommendation_type=recommendation_type
                )
                db.add(recommendation)
                db.commit()
                db.refresh(recommendation)
                return recommendation
            except Exception as e:
                db.rollback()
                raise Exception(f"Failed to create recommendation: {str(e)}")

        def get_top_recommendations(self, db: Session, user_id: int, limit: int = 10) -> list[Recommendation]:
            """Retrieves top N recommendations for a user ordered by score."""
            return db.query(Recommendation)\
                .filter(Recommendation.user_id == user_id)\
                .order_by(Recommendation.score.desc())\
                .limit(limit)\
                .all()

        def delete_old_recommendations(self, db: Session, user_id: int, days: int = 30) -> int:
            """Removes recommendations older than specified days."""
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = db.query(Recommendation)\
                .filter(Recommendation.user_id == user_id)\
                .filter(Recommendation.created_at < cutoff_date)\
                .delete()
            db.commit()
            return result