from typing import Any, Dict, List, Optional, Union
import re
import json
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
import logging
from dataclasses import dataclass

@dataclass
class ValidationError:
    field: str
    message: str

class InputValidator:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._errors: List[ValidationError] = []

    @property
    def errors(self) -> List[ValidationError]:
        return self._errors

    def has_errors(self) -> bool:
        return len(self._errors) > 0

    def _add_error(self, field: str, message: str) -> None:
        self._errors.append(ValidationError(field=field, message=message))
        self._logger.warning(f"Validation error: {field} - {message}")

    def validate_required(self, value: Any, field: str) -> bool:
        if value is None or (isinstance(value, str) and not value.strip()):
            self._add_error(field, "This field is required")
            return False
        return True

    def validate_string(self, value: str, field: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        if not isinstance(value, str):
            self._add_error(field, "Value must be a string")
            return False
        
        if len(value.strip()) < min_length:
            self._add_error(field, f"Minimum length is {min_length} characters")
            return False
        
        if max_length and len(value) > max_length:
            self._add_error(field, f"Maximum length is {max_length} characters")
            return False
        
        return True

    def validate_email(self, value: str, field: str) -> bool:
        try:
            validate_email(value)
            return True
        except EmailNotValidError:
            self._add_error(field, "Invalid email format")
            return False

    def validate_numeric(self, value: Union[int, float], field: str, 
                        min_value: Optional[float] = None, 
                        max_value: Optional[float] = None) -> bool:
        if not isinstance(value, (int, float)):
            self._add_error(field, "Value must be numeric")
            return False

        if min_value is not None and value < min_value:
            self._add_error(field, f"Value must be greater than or equal to {min_value}")
            return False

        if max_value is not None and value > max_value:
            self._add_error(field, f"Value must be less than or equal to {max_value}")
            return False

        return True

    def validate_date(self, value: str, field: str, format: str = "%Y-%m-%d") -> bool:
        try:
            datetime.strptime(value, format)
            return True
        except ValueError:
            self._add_error(field, f"Invalid date format. Expected format: {format}")
            return False

    def validate_regex(self, value: str, field: str, pattern: str, message: str) -> bool:
        if not re.match(pattern, value):
            self._add_error(field, message)
            return False
        return True

    def validate_json(self, value: str, field: str) -> bool:
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            self._add_error(field, "Invalid JSON format")
            return False

    def validate_in_list(self, value: Any, field: str, valid_values: List[Any]) -> bool:
        if value not in valid_values:
            self._add_error(field, f"Value must be one of: {', '.join(map(str, valid_values))}")
            return False
        return True

    def validate_dict_schema(self, data: Dict, schema: Dict[str, Dict[str, Any]]) -> bool:
        """
        Validates a dictionary against a schema
        Schema format: {
            'field_name': {
                'type': str/int/float,
                'required': bool,
                'min_length': int,
                'max_length': int,
                'min_value': number,
                'max_value': number,
                'pattern': str,
                'values': list
            }
        }
        """
        is_valid = True
        
        for field, rules in schema.items():
            value = data.get(field)
            
            if rules.get('required', False):
                if not self.validate_required(value, field):
                    is_valid = False
                    continue

            if value is not None:
                if rules.get('type') == str:
                    is_valid &= self.validate_string(
                        value, field,
                        rules.get('min_length', 0),
                        rules.get('max_length')
                    )
                elif rules.get('type') in (int, float):
                    is_valid &= self.validate_numeric(
                        value, field,
                        rules.get('min_value'),
                        rules.get('max_value')
                    )
                
                if rules.get('pattern'):
                    is_valid &= self.validate_regex(
                        value, field,
                        rules['pattern'],
                        rules.get('pattern_message', 'Invalid format')
                    )
                
                if rules.get('values'):
                    is_valid &= self.validate_in_list(
                        value, field,
                        rules['values']
                    )

        return is_valid

    def is_valid_input(self, user_id: str, query: str) -> bool:
        # Exemplo simples de validação
        if not user_id or not isinstance(user_id, str):
            return False
        if not query or not isinstance(query, str):
            return False
        return True