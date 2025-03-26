from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from repositories.base_repository import BaseRepository
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def get_logs(self, db: Session, limit: int = 50):
        """ Retorna os logs de auditoria mais recentes. """
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
        def create_audit_log(self, db: Session, action: str, entity: str, entity_id: str, user_id: str, details: dict = None) -> AuditLog:
            """Creates a new audit log entry with comprehensive tracking.

            Args:
                db (Session): Database session
                action (str): The action performed (e.g., 'CREATE', 'UPDATE', 'DELETE')
                entity (str): The entity type being audited
                entity_id (str): Identifier of the affected entity
                user_id (str): ID of the user performing the action
                details (dict, optional): Additional context information

            Returns:
                AuditLog: Created audit log entry
            """
            audit_entry = AuditLog(
                action=action,
                entity=entity,
                entity_id=entity_id,
                user_id=user_id,
                details=details
            )
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            return audit_entry

        def get_entity_history(self, db: Session, entity: str, entity_id: str) -> list[AuditLog]:
            """Retrieves complete audit history for a specific entity.

            Args:
                db (Session): Database session
                entity (str): Entity type to query
                entity_id (str): Entity identifier

            Returns:
                list[AuditLog]: List of audit logs for the entity
            """
            return (db.query(AuditLog)
                    .filter(AuditLog.entity == entity,
                           AuditLog.entity_id == entity_id)
                    .order_by(AuditLog.timestamp.desc())
                    .all())

        def search_logs(self, db: Session, **filters) -> list[AuditLog]:
            """Advanced search functionality for audit logs.

            Args:
                db (Session): Database session
                **filters: Dynamic filters (e.g., action, user_id, date_range)

            Returns:
                list[AuditLog]: Filtered audit logs
            """
            query = db.query(AuditLog)
            
            for key, value in filters.items():
                if hasattr(AuditLog, key) and value is not None:
                    query = query.filter(getattr(AuditLog, key) == value)
                    
            return query.order_by(AuditLog.timestamp.desc()).all()