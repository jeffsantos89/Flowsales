from jsonschema import validate, ValidationError
from datetime import datetime
from typing import Dict, Optional, Any
from logging import getLogger
from copy import deepcopy

# Configure logging
logger = getLogger("EventValidator")

class EventValidationError(Exception):
    """Custom exception for event validation errors"""
    pass

# Base schema with strict typing and format validation
EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "minLength": 1
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "data": {
            "type": "object",
            "minProperties": 1
        },
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$"
        }
    },
    "required": ["type", "timestamp", "data", "version"],
    "additionalProperties": False
}

class EventValidator:
    """Event validation handler with enhanced validation capabilities"""
    
    @staticmethod
    def is_valid_timestamp(timestamp_str: str) -> bool:
        """
        Validates if a timestamp string is in ISO 8601 format
        
        Args:
            timestamp_str: String timestamp to validate
            
        Returns:
            bool: True if timestamp is valid
        """
        try:
            datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def validate_event(cls, event: Dict[str, Any]) -> bool:
        """
        Validates an event against the base schema
        
        Args:
            event: Event dictionary to validate
            
        Returns:
            bool: True if event is valid
            
        Raises:
            EventValidationError: If validation fails
        """
        try:
            if not isinstance(event, dict):
                raise EventValidationError("Event must be a dictionary")

            validate(instance=event, schema=EVENT_SCHEMA)

            if not cls.is_valid_timestamp(event.get("timestamp", "")):
                raise EventValidationError("Invalid ISO 8601 timestamp format")

            logger.info(f"Event validation successful - Type: {event.get('type')}, Version: {event.get('version')}")
            return True

        except ValidationError as e:
            logger.error(f"Schema validation failed: {str(e)}")
            raise EventValidationError(f"Schema validation error: {e.message}")
        except Exception as e:
            logger.exception("Unexpected validation error")
            raise EventValidationError(f"Unexpected validation error: {str(e)}")

    @classmethod
    def validate_event_strict(
        cls, 
        event: Dict[str, Any], 
        additional_schema: Optional[Dict] = None,
        allow_additional_properties: bool = False
    ) -> bool:
        """
        Enhanced validation with custom schema support
        
        Args:
            event: Event dictionary to validate
            additional_schema: Additional schema rules to apply
            allow_additional_properties: Whether to allow properties not in schema
            
        Returns:
            bool: True if validation passes
            
        Raises:
            EventValidationError: If validation fails
        """
        try:
            if not isinstance(event, dict):
                raise EventValidationError("Event must be a dictionary")

            # Create deep copy to avoid modifying original schema
            schema = deepcopy(EVENT_SCHEMA)
            
            if additional_schema:
                schema["properties"].update(additional_schema)
            
            schema["additionalProperties"] = allow_additional_properties

            validate(instance=event, schema=schema)
            cls.validate_event(event)  # Run base validation as well
            
            logger.info("Enhanced validation successful with custom schema")
            return True

        except (ValidationError, EventValidationError) as e:
            logger.error(f"Enhanced validation failed: {str(e)}")
            raise EventValidationError(f"Enhanced validation error: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error in enhanced validation")
            raise EventValidationError(f"Unexpected error in enhanced validation: {str(e)}")
