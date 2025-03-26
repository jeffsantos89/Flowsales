import re
from typing import Any, Dict, List, Union

class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass

class DataValidator:
    """A class for validating various types of data."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate an email address."""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, email):
            raise DataValidationError(f"Invalid email address: {email}")
        return True

    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        """Validate a phone number."""
        pattern = r'^\+?1?\d{9,15}$'
        if not re.match(pattern, phone_number):
            raise DataValidationError(f"Invalid phone number: {phone_number}")
        return True

    @staticmethod
    def validate_non_empty_string(value: str, field_name: str) -> bool:
        """Validate that a string is not empty."""
        if not value or not isinstance(value, str):
            raise DataValidationError(f"{field_name} cannot be empty.")
        return True

    @staticmethod
    def validate_integer(value: Any, field_name: str) -> bool:
        """Validate that a value is an integer."""
        if not isinstance(value, int):
            raise DataValidationError(f"{field_name} must be an integer.")
        return True

    @staticmethod
    def validate_positive_number(value: Union[int, float], field_name: str) -> bool:
        """Validate that a number is positive."""
        if not isinstance(value, (int, float)) or value <= 0:
            raise DataValidationError(f"{field_name} must be a positive number.")
        return True

    @staticmethod
    def validate_list_of_dicts(data: List[Dict[str, Any]], schema: Dict[str, Any]) -> bool:
        """Validate a list of dictionaries against a schema."""
        if not isinstance(data, list):
            raise DataValidationError("Data must be a list of dictionaries.")
        for item in data:
            if not isinstance(item, dict):
                raise DataValidationError("Each item in the list must be a dictionary.")
            for key, validator in schema.items():
                if key not in item:
                    raise DataValidationError(f"Missing required field: {key}")
                validator(item[key], key)
        return True

    @staticmethod
    def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate a dictionary against a schema."""
        if not isinstance(data, dict):
            raise DataValidationError("Data must be a dictionary.")
        for key, validator in schema.items():
            if key not in data:
                raise DataValidationError(f"Missing required field: {key}")
            validator(data[key], key)
        return True