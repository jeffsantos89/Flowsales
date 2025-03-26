from sqlalchemy.orm import Session
from repositories.whatsapp_repository import WhatsappRepository
from models.whatsapp_logs import WhatsappLog

whatsapp_repo = WhatsappRepository()

def save_whatsapp_message(db: Session, user_id: int, message: str):
    """ Salva uma nova mensagem no banco. """
    log_entry = WhatsappLog(user_id=user_id, message=message)
    return whatsapp_repo.create(db, log_entry)

def get_whatsapp_history(db: Session, user_id: int):
    """ Retorna o histórico de conversas de um usuário. """
    return whatsapp_repo.get_logs_by_user(db, user_id)
    class WhatsappService:
        def __init__(self):
            self.repository = WhatsappRepository()

        async def save_message(self, db: Session, user_id: int, message: str) -> WhatsappLog:
            """
            Saves a new WhatsApp message to the database.
            
            Args:
                db (Session): Database session
                user_id (int): ID of the user
                message (str): Message content
                
            Returns:
                WhatsappLog: Created log entry
            """
            try:
                log_entry = WhatsappLog(user_id=user_id, message=message)
                return await self.repository.create(db, log_entry)
            except Exception as e:
                logger.error(f"Error saving message: {str(e)}")
                raise

        async def get_history(self, db: Session, user_id: int, 
                             limit: int = 100, offset: int = 0) -> list[WhatsappLog]:
            """
            Retrieves paginated message history for a user.
            
            Args:
                db (Session): Database session
                user_id (int): ID of the user
                limit (int): Maximum number of messages to return
                offset (int): Number of messages to skip
                
            Returns:
                list[WhatsappLog]: List of message logs
            """
            try:
                return await self.repository.get_logs_by_user(
                    db, user_id, limit=limit, offset=offset
                )
            except Exception as e:
                logger.error(f"Error retrieving history: {str(e)}")
                raise