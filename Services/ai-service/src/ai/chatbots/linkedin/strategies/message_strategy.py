"""
message_strategy.py
Advanced strategy for handling general LinkedIn messages with robust error handling and response management.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json

from base import BaseLinkedInStrategy
from utils.logger import logger
from exceptions import MessageProcessingError, InvalidMessageFormat

class ConversationState(Enum):
    INITIAL = "initial"
    MESSAGING = "messaging"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class MessageContext:
    user_id: str
    message_text: str
    timestamp: datetime
    conversation_id: str
    metadata: Dict[str, Any]

class MessageStrategy(BaseLinkedInStrategy):
    """
    Sophisticated handler for generic conversations on LinkedIn with advanced features:
    - Robust error handling
    - Message validation
    - Conversation state management
    - Detailed logging
    - Response templating
    """

    MAX_MESSAGE_LENGTH = 1000
    MIN_MESSAGE_LENGTH = 1

    def __init__(self):
        super().__init__()
        self.response_templates = self._load_response_templates()

    def _load_response_templates(self) -> Dict[str, str]:
        try:
            with open('config/response_templates.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Response templates file not found. Using default templates.")
            return {
                "default": "Recebi sua mensagem: '{message}'. Como posso ajudar?",
                "error": "Desculpe, ocorreu um erro ao processar sua mensagem.",
                "too_long": "Sua mensagem é muito longa. Por favor, seja mais conciso."
            }

    def _validate_message(self, message_text: str) -> bool:
        if not message_text:
            raise InvalidMessageFormat("Message text cannot be empty")
        if len(message_text) > self.MAX_MESSAGE_LENGTH:
            raise InvalidMessageFormat("Message exceeds maximum length")
        if len(message_text) < self.MIN_MESSAGE_LENGTH:
            raise InvalidMessageFormat("Message is too short")
        return True

    def _create_message_context(self, user_id: str, message_text: str, 
                              conversation: Dict[str, Any]) -> MessageContext:
        return MessageContext(
            user_id=user_id,
            message_text=message_text,
            timestamp=datetime.now(),
            conversation_id=conversation.get('id', ''),
            metadata=conversation.get('metadata', {})
        )

    def _process_message(self, context: MessageContext) -> Dict[str, Any]:
        """Process the message and determine appropriate response."""
        # Add your custom message processing logic here
        return {
            "response_type": "message",
            "message": self.response_templates["default"].format(message=context.message_text),
            "conversation_state": ConversationState.MESSAGING.value,
            "processed_at": context.timestamp.isoformat(),
            "metadata": {
                "user_id": context.user_id,
                "conversation_id": context.conversation_id
            }
        }

    def execute(self, user_id: str, message_text: str, 
                conversation: Dict[str, Any], query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the message strategy with comprehensive error handling and logging.
        """
        try:
            logger.info(f"[MessageStrategy] Processing message from user_id={user_id}")
            
            # Validate message
            self._validate_message(message_text)

            # Create message context
            context = self._create_message_context(user_id, message_text, conversation)

            # Process message and generate response
            response = self._process_message(context)

            logger.info(f"[MessageStrategy] Successfully processed message for user_id={user_id}")
            return response

        except InvalidMessageFormat as e:
            logger.warning(f"[MessageStrategy] Invalid message format: {str(e)}")
            return {
                "response_type": "error",
                "message": self.response_templates.get("too_long", str(e)),
                "conversation_state": ConversationState.ERROR.value
            }
        except Exception as e:
            logger.error(f"[MessageStrategy] Error processing message: {str(e)}", exc_info=True)
            return {
                "response_type": "error",
                "message": self.response_templates["error"],
                "conversation_state": ConversationState.ERROR.value
            }
