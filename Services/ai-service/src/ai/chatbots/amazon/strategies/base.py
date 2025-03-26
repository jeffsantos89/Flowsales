"""
base.py
Define a classe base abstrata para as estratégias de e-commerce do AmazonBot.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from datetime import datetime

class BaseAmazonStrategy(ABC):
    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recebe um payload com dados necessários e retorna um dicionário
        com o resultado do processamento.
        """
        pass
        def __init__(self):
            self._logger = logging.getLogger(self.__class__.__name__)
            self.metadata = {}

        @property
        def strategy_name(self) -> str:
            return self.__class__.__name__

        def validate_payload(self, payload: Dict[str, Any]) -> None:
            """Validate incoming payload data"""
            if not isinstance(payload, dict):
                raise ValueError("Payload must be a dictionary")

        def pre_execute(self, payload: Dict[str, Any]) -> None:
            """Hook for pre-execution tasks"""
            self._logger.info(f"Starting {self.strategy_name} execution")
            self.metadata['start_time'] = datetime.utcnow()
            self.validate_payload(payload)

        def post_execute(self, result: Dict[str, Any]) -> None:
            """Hook for post-execution tasks"""
            self.metadata['end_time'] = datetime.utcnow()
            self.metadata['duration'] = self.metadata['end_time'] - self.metadata['start_time']
            self._logger.info(f"Completed {self.strategy_name} execution")

        def safe_execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
            """Template method with error handling"""
            try:
                self.pre_execute(payload)
                result = self.execute(payload)
                self.post_execute(result)
                return result
            except Exception as e:
                self._logger.error(f"Error in {self.strategy_name}: {str(e)}")
                raise