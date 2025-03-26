from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import random
import time
from enum import Enum
from functools import wraps
import json
from threading import Lock

class PostValidationError(Exception):
    """Custom exception for post validation failures"""
    pass

class CommentGenerationError(Exception):
    """Custom exception for comment generation failures"""
    pass

class CommentPublishError(Exception):
    """Custom exception for comment publishing failures"""
    pass

class PostType(Enum):
    """Enum for different types of posts"""
    PHOTO = "photo"
    VIDEO = "video"
    REEL = "reel"
    STORY = "story"
    CAROUSEL = "carousel"

@dataclass
class CommentConfig:
    """Configuration for comment strategy"""
    max_comments_per_post: int = 3
    min_delay: float = 2.0
    max_delay: float = 5.0
    max_retries: int = 3
    comment_templates: List[str] = field(default_factory=list)
    blacklist_words: List[str] = field(default_factory=list)
    enable_rate_limiting: bool = True
    rate_limit_period: int = 3600  # 1 hour
    max_comments_per_period: int = 50
    comment_timeout: float = 30.0

    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.min_delay > self.max_delay:
            raise ValueError("min_delay cannot be greater than max_delay")
        if self.max_comments_per_post < 1:
            raise ValueError("max_comments_per_post must be at least 1")

def retry_with_backoff(max_retries: int, initial_delay: float = 1.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator

class RateLimiter:
    """Rate limiter implementation"""
    def __init__(self, period: int, max_calls: int):
        self.period = period
        self.max_calls = max_calls
        self.calls = []
        self._lock = Lock()

    def is_allowed(self) -> bool:
        with self._lock:
            now = time.time()
            self.calls = [call for call in self.calls if call > now - self.period]
            if len(self.calls) >= self.max_calls:
                return False
            self.calls.append(now)
            return True

class CommentStrategy(ABC):
    """Abstract base class for comment strategies"""
    
    @abstractmethod
    def execute(self, post_data: Dict[str, Any]) -> bool:
        """Execute comment strategy"""
        pass

    @abstractmethod
    def can_comment(self, post_data: Dict[str, Any]) -> bool:
        """Check if commenting is allowed"""
        pass

class InstagramCommentStrategy(CommentStrategy):
    """Instagram comment strategy implementation"""
    
    def __init__(self, instagram_client: Any, config: Optional[CommentConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.instagram_client = instagram_client
        self.config = config or CommentConfig()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_period,
            self.config.max_comments_per_period
        )
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging with structured format"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def can_comment(self, post_data: Dict[str, Any]) -> bool:
        """Check if commenting is allowed based on rate limits and validation"""
        if self.config.enable_rate_limiting and not self.rate_limiter.is_allowed():
            self.logger.warning("Rate limit exceeded")
            return False
        return self._validate_post(post_data)

    def _validate_post(self, post_data: Dict[str, Any]) -> bool:
        """Enhanced post validation with detailed checks"""
        try:
            required_fields = ['id', 'caption', 'username']
            if not all(field in post_data for field in required_fields):
                raise PostValidationError(f"Missing required fields: {required_fields}")

            if self.config.blacklist_words:
                text_content = f"{post_data['caption']} {post_data.get('comments', '')}".lower()
                blacklisted = [word for word in self.config.blacklist_words if word.lower() in text_content]
                if blacklisted:
                    raise PostValidationError(f"Contains blacklisted words: {blacklisted}")

            return True
        except Exception as e:
            self.logger.error(f"Post validation failed: {str(e)}")
            return False

    @retry_with_backoff(max_retries=3)
    def _generate_comment(self, post_data: Dict[str, Any]) -> str:
        """Generate comment with enhanced template handling"""
        try:
            if not self.config.comment_templates:
                raise CommentGenerationError("No comment templates available")

            template = random.choice(self.config.comment_templates)
            post_type = PostType(post_data.get('type', 'photo')).value
            
            return template.format(
                username=post_data['username'],
                post_type=post_type,
                **post_data
            )
        except Exception as e:
            raise CommentGenerationError(f"Failed to generate comment: {str(e)}")

    @retry_with_backoff(max_retries=3)
    def _add_comment(self, post_id: str, comment: str) -> bool:
        """Add comment with enhanced error handling and retry logic"""
        try:
            delay = random.uniform(self.config.min_delay, self.config.max_delay)
            time.sleep(delay)

            success = self.instagram_client.add_comment(
                post_id=post_id,
                comment=comment,
                timeout=self.config.comment_timeout
            )

            if not success:
                raise CommentPublishError("Comment publish failed")

            self.logger.info(f"Successfully commented on post {post_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add comment: {str(e)}")
            raise CommentPublishError(str(e))

    def execute(self, post_data: Dict[str, Any]) -> bool:
        """Execute comment strategy with comprehensive error handling"""
        try:
            if not self.can_comment(post_data):
                return False

            comment = self._generate_comment(post_data)
            return self._add_comment(post_data['id'], comment)

        except (PostValidationError, CommentGenerationError, CommentPublishError) as e:
            self.logger.error(f"Strategy execution failed: {str(e)}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error in strategy execution: {str(e)}")
            return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(config={json.dumps(self.config.__dict__, default=str)})"
