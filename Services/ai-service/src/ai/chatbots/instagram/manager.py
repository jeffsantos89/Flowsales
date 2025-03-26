import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from enum import Enum

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s'
)
logger = logging.getLogger(__name__)

class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class MessageContext:
    user_id: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: MessageStatus = field(default=MessageStatus.PENDING)
    retries: int = field(default=0)
    error: Optional[str] = field(default=None)

class MessageHandler(ABC):
    @abstractmethod
    async def handle_message(self, context: MessageContext) -> str:
        pass

    @abstractmethod
    async def on_error(self, context: MessageContext, error: Exception) -> None:
        pass

class InstagramBotManager:
    def __init__(
        self,
        message_handler: MessageHandler,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        concurrent_limit: int = 10,
        session_timeout_hours: int = 24,
        cleanup_interval: int = 3600  # Cleanup every hour
    ):
        self._message_handler = message_handler
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._concurrent_limit = concurrent_limit
        self._session_timeout = session_timeout_hours * 3600
        self._cleanup_interval = cleanup_interval
        self._active_sessions: Dict[str, datetime] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(concurrent_limit)
        self._running = False
        self._tasks: List[asyncio.Task] = []
        self._metrics: Dict[str, int] = {
            "messages_processed": 0,
            "errors": 0,
            "active_sessions": 0
        }

    @asynccontextmanager
    async def session(self):
        """Context manager for managing bot lifecycle"""
        try:
            await self.start()
            yield self
        finally:
            await self.stop()

    async def start(self):
        """Start the Instagram bot manager and background tasks"""
        if self._running:
            return

        self._running = True
        self._tasks.extend([
            asyncio.create_task(self._cleanup_loop()),
            asyncio.create_task(self._message_processor())
        ])
        logger.info("Instagram bot manager started successfully")

    async def stop(self):
        """Gracefully stop the Instagram bot manager"""
        if not self._running:
            return

        self._running = False
        
        # Cancel all background tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        # Clean up resources
        self._active_sessions.clear()
        logger.info("Instagram bot manager stopped successfully")

    async def process_message(self, user_id: str, message: str) -> Optional[str]:
        """Queue message for processing"""
        if not self._running:
            raise RuntimeError("Instagram bot manager is not running")

        context = MessageContext(user_id=user_id, message=message)
        await self._message_queue.put(context)
        return await self._process_single_message(context)

    async def _process_single_message(self, context: MessageContext) -> Optional[str]:
        """Process a single message with retry logic and rate limiting"""
        async with self._semaphore:
            context.status = MessageStatus.PROCESSING
            
            for attempt in range(self._max_retries):
                try:
                    context.retries = attempt + 1
                    response = await self._message_handler.handle_message(context)
                    self._update_session(context.user_id)
                    context.status = MessageStatus.COMPLETED
                    self._metrics["messages_processed"] += 1
                    return response
                except Exception as e:
                    context.error = str(e)
                    logger.error(f"Error processing message (attempt {attempt + 1}/{self._max_retries}): {str(e)}")
                    await self._message_handler.on_error(context, e)
                    
                    if attempt < self._max_retries - 1:
                        await asyncio.sleep(self._retry_delay * (attempt + 1))  # Exponential backoff
                    else:
                        context.status = MessageStatus.FAILED
                        self._metrics["errors"] += 1
                        raise

    async def _cleanup_loop(self):
        """Background task for cleaning up expired sessions"""
        while self._running:
            try:
                self.cleanup_old_sessions()
                await asyncio.sleep(self._cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")

    async def _message_processor(self):
        """Background task for processing queued messages"""
        while self._running:
            try:
                context = await self._message_queue.get()
                await self._process_single_message(context)
                self._message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message processor: {str(e)}")

    def _update_session(self, user_id: str):
        """Update user session timestamp"""
        self._active_sessions[user_id] = datetime.utcnow()
        self._metrics["active_sessions"] = len(self._active_sessions)

    def cleanup_old_sessions(self):
        """Clean up inactive sessions"""
        current_time = datetime.utcnow()
        expired_sessions = [
            user_id for user_id, timestamp in self._active_sessions.items()
            if (current_time - timestamp).total_seconds() > self._session_timeout
        ]
        for user_id in expired_sessions:
            del self._active_sessions[user_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        self._metrics["active_sessions"] = len(self._active_sessions)

    async def get_status(self) -> Dict[str, Any]:
        """Get detailed status of the bot manager"""
        return {
            "running": self._running,
            "active_sessions": self.active_sessions_count,
            "concurrent_limit": self._concurrent_limit,
            "queue_size": self._message_queue.qsize(),
            "metrics": self._metrics,
            "background_tasks": len(self._tasks)
        }

    @property
    def active_sessions_count(self) -> int:
        return len(self._active_sessions)
