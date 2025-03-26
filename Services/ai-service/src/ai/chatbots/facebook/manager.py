import logging
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FacebookMessageHandler(ABC):
    @abstractmethod
    async def handle_message(self, sender_id: str, message_data: Dict[str, Any]) -> None:
        pass

class FacebookChatbotManager:
    """
    A sophisticated Facebook chatbot manager that handles message processing,
    error handling, and maintains conversation state.
    """
    
    def __init__(self, access_token: str, verify_token: str):
        self._access_token = access_token
        self._verify_token = verify_token
        self._message_handlers: Dict[str, FacebookMessageHandler] = {}
        self._conversation_states: Dict[str, Dict[str, Any]] = {}
        self._rate_limits: Dict[str, datetime] = {}
        self._MAX_RETRIES = 3
        self._RATE_LIMIT_WINDOW = 60  # seconds

    async def verify_webhook(self, mode: str, token: str) -> bool:
        """Verify webhook subscription."""
        try:
            return mode == "subscribe" and token == self._verify_token
        except Exception as e:
            logger.error(f"Webhook verification failed: {str(e)}")
            return False

    async def process_webhook_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming webhook events."""
        try:
            if 'object' not in event_data or event_data['object'] != 'page':
                logger.warning("Received invalid webhook event")
                return None

            for entry in event_data.get('entry', []):
                await self._process_entry(entry)

            return {"status": "ok"}

        except Exception as e:
            logger.error(f"Error processing webhook event: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _process_entry(self, entry: Dict[str, Any]) -> None:
        """Process a single webhook entry."""
        try:
            messaging = entry.get('messaging', [])
            for message_event in messaging:
                sender_id = message_event.get('sender', {}).get('id')
                if not sender_id:
                    continue

                if not self._check_rate_limit(sender_id):
                    logger.warning(f"Rate limit exceeded for sender {sender_id}")
                    continue

                await self._handle_message_event(sender_id, message_event)

        except Exception as e:
            logger.error(f"Error processing entry: {str(e)}")

    async def _handle_message_event(self, sender_id: str, message_event: Dict[str, Any]) -> None:
        """Handle different types of message events."""
        try:
            if 'message' in message_event:
                await self._process_message(sender_id, message_event['message'])
            elif 'postback' in message_event:
                await self._process_postback(sender_id, message_event['postback'])

        except Exception as e:
            logger.error(f"Error handling message event: {str(e)}")

    def register_handler(self, message_type: str, handler: FacebookMessageHandler) -> None:
        """Register a message handler for a specific message type."""
        self._message_handlers[message_type] = handler

    def _check_rate_limit(self, sender_id: str) -> bool:
        """Check if sender has exceeded rate limit."""
        now = datetime.now()
        if sender_id in self._rate_limits:
            time_diff = (now - self._rate_limits[sender_id]).total_seconds()
            if time_diff < self._RATE_LIMIT_WINDOW:
                return False
        self._rate_limits[sender_id] = now
        return True

    async def send_message(self, recipient_id: str, message_data: Dict[str, Any]) -> bool:
        """Send message to recipient with retry logic."""
        for attempt in range(self._MAX_RETRIES):
            try:
                # Implement actual message sending logic here
                # This is a placeholder for the actual API call
                logger.info(f"Sending message to {recipient_id}: {json.dumps(message_data)}")
                return True

            except Exception as e:
                if attempt == self._MAX_RETRIES - 1:
                    logger.error(f"Failed to send message after {self._MAX_RETRIES} attempts: {str(e)}")
                    return False
                await asyncio.sleep(1 * (attempt + 1))

    def get_conversation_state(self, sender_id: str) -> Dict[str, Any]:
        """Get the current conversation state for a sender."""
        return self._conversation_states.get(sender_id, {})

    def update_conversation_state(self, sender_id: str, state_data: Dict[str, Any]) -> None:
        """Update the conversation state for a sender."""
        if sender_id not in self._conversation_states:
            self._conversation_states[sender_id] = {}
        self._conversation_states[sender_id].update(state_data)

    async def _process_message(self, sender_id: str, message_data: Dict[str, Any]) -> None:
        """Process text messages."""
        handler = self._message_handlers.get('message')
        if handler:
            await handler.handle_message(sender_id, message_data)

    async def _process_postback(self, sender_id: str, postback_data: Dict[str, Any]) -> None:
        """Process postback messages."""
        handler = self._message_handlers.get('postback')
        if handler:
            await handler.handle_message(sender_id, postback_data)

    def cleanup_old_conversations(self, max_age_hours: int = 24) -> None:
        """Clean up old conversation states."""
        now = datetime.now()
        to_remove = []
        
        for sender_id, state in self._conversation_states.items():
            last_interaction = state.get('last_interaction')
            if last_interaction and (now - last_interaction).total_seconds() > max_age_hours * 3600:
                to_remove.append(sender_id)

        for sender_id in to_remove:
            del self._conversation_states[sender_id]