import json
from typing import Any, Dict, List, Union

class JSONUtils:
    @staticmethod
    def read_json(file_path: str) -> Union[Dict[str, Any], List[Any]]:
        """
        Reads a JSON file and returns its content.
        
        :param file_path: Path to the JSON file.
        :return: Parsed JSON content as a dictionary or list.
        :raises FileNotFoundError: If the file does not exist.
        :raises json.JSONDecodeError: If the file content is not valid JSON.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {file_path}") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON content in file: {file_path}", e.doc, e.pos)

    @staticmethod
    def write_json(data: Union[Dict[str, Any], List[Any]], file_path: str, indent: int = 4) -> None:
        """
        Writes data to a JSON file.
        
        :param data: Data to write to the JSON file.
        :param file_path: Path to the JSON file.
        :param indent: Indentation level for pretty-printing the JSON data.
        :raises TypeError: If the data is not serializable to JSON.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=indent)
        except TypeError as e:
            raise TypeError(f"Data is not serializable to JSON: {data}") from e

    @staticmethod
    def update_json(file_path: str, updates: Dict[str, Any]) -> None:
        """
        Updates a JSON file with new data.
        
        :param file_path: Path to the JSON file.
        :param updates: Dictionary containing the updates.
        :raises FileNotFoundError: If the file does not exist.
        :raises json.JSONDecodeError: If the file content is not valid JSON.
        """
        try:
            data = JSONUtils.read_json(file_path)
            if not isinstance(data, dict):
                raise ValueError("JSON content must be a dictionary to update")
            data.update(updates)
            JSONUtils.write_json(data, file_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {file_path}") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON content in file: {file_path}", e.doc, e.pos)
        except ValueError as e:
            raise ValueError(f"Error updating JSON file: {e}") from e

    @staticmethod
    def validate_json(data: Union[Dict[str, Any], List[Any]]) -> bool:
        """
        Validates if the data is serializable to JSON.
        
        :param data: Data to validate.
        :return: True if data is valid JSON, False otherwise.
        """
        try:
            json.dumps(data)
            return True
        except (TypeError, OverflowError):
            return False