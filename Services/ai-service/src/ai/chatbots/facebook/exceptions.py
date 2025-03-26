from typing import Optional
from datetime import datetime

# filepath: c:\Users\jeferson\Desktop\Flowsale\Services\ai-service\src\ai\exceptions.py



class FacebookBotBaseException(Exception):
    """Base exception class for all Facebook bot related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None) -> None:
        self.message = message
        self.error_code = error_code
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message} (at {self.timestamp.isoformat()})"


class PostbackProcessingError(FacebookBotBaseException):
    """Exception raised when there's an error processing a postback."""
    
    def __init__(self, message: str, postback_payload: Optional[str] = None) -> None:
        error_code = "FB_POSTBACK_001"
        self.postback_payload = postback_payload
        super().__init__(message=message, error_code=error_code)

    def get_error_context(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "timestamp": self.timestamp,
            "postback_payload": self.postback_payload
        }


class InvalidPayloadError(FacebookBotBaseException):
    """Exception raised when a postback payload is invalid or malformed."""
    
    def __init__(self, message: str, payload: Optional[str] = None, validation_errors: Optional[list] = None) -> None:
        error_code = "FB_PAYLOAD_001"
        self.payload = payload
        self.validation_errors = validation_errors or []
        super().__init__(message=message, error_code=error_code)

    def get_error_context(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "validation_errors": self.validation_errors
        }