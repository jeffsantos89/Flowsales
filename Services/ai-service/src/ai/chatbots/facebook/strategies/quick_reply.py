"""
quick_reply.py
Estratégia de processamento para quick replies (respostas rápidas) do Messenger.
"""
from typing import Dict, Any
from .base import BaseFacebookStrategy
from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task


class QuickReplyStrategy(BaseFacebookStrategy):
    """
    Estratégia para lidar com Quick Replies do Messenger.
    Pode extrair payloads específicos para fluxo de decisão.
    """

    @retry(max_attempts=2, backoff=1)
    @background_task
    def process(self, message_payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            quick_reply_data = message_payload.get("quick_reply", {})
            user_id = message_payload.get("user_id", "desconhecido")
            logger.debug(f"[QuickReplyStrategy] Processando quick reply de {user_id}: {quick_reply_data}")

            # Exemplo: extrair o payload da quick reply
            payload = quick_reply_data.get("payload", "N/A")
            return {
                "quick_reply_payload": payload,
                "user_id": user_id
            }

        except Exception as e:
            logger.exception("[QuickReplyStrategy] Erro ao processar quick reply")
            return {
                "error": str(e),
                "user_id": message_payload.get("user_id", "desconhecido")
            }
