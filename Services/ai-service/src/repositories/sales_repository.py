from sqlalchemy.orm import Session
from models.sales import Sales
from repositories.base_repository import BaseRepository
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

class SalesRepository(BaseRepository[Sales]):
    def __init__(self):
        super().__init__(Sales)

    def get_sales_by_date(self, db: Session, start_date, end_date):
        """ Retorna vendas dentro de um período. """
        return db.query(Sales).filter(Sales.date >= start_date, Sales.date <= end_date).all()

    def get_sales_by_customer(self, db: Session, customer_id: int):
        """Get all sales for a specific customer."""
        return db.query(Sales).filter(Sales.customer_id == customer_id).all()

    def get_sales_by_status(self, db: Session, status: str):
        """Get sales by their status."""
        return db.query(Sales).filter(Sales.status == status).all()

    def get_total_sales_amount(self, db: Session, start_date=None, end_date=None):
        """Calculate total sales amount with optional date range."""
        query = db.query(Sales)
        if start_date and end_date:
            query = query.filter(Sales.date.between(start_date, end_date))
        return sum(sale.amount for sale in query.all())

    def get_sales_with_pagination(self, db: Session, skip: int = 0, limit: int = 100):
        """Get paginated sales results."""
        return db.query(Sales).offset(skip).limit(limit).all()

    def search_sales(self, db: Session, **filters):
        """Flexible search with multiple filter criteria."""
        query = db.query(Sales)
        for key, value in filters.items():
            if hasattr(Sales, key) and value is not None:
                query = query.filter(getattr(Sales, key) == value)
        return query.all()

    def get_recent_sales(self, db: Session, limit: int = 10):
        """Get most recent sales."""
        return db.query(Sales).order_by(Sales.date.desc()).limit(limit).all()