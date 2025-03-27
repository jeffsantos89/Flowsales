import logging
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential
from dataclasses import dataclass
import json
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GoogleServiceConfig:
    """Configuration class for Google services"""
    credentials_path: str
    scopes: list[str]
    api_version: str
    service_name: str

class GoogleClientError(Exception):
    """Custom exception for Google Client errors"""
    pass

class GoogleClient:
    """
    A robust and scalable Google API client implementation
    with retry mechanisms and proper error handling.
    """

    def __init__(self, config: GoogleServiceConfig):
        """
        Initialize the Google Client with the provided configuration.
        
        Args:
            config (GoogleServiceConfig): Configuration object containing service details
        """
        self.config = config
        self._service = None
        self._credentials = None
        self.initialize_client()

    def initialize_client(self) -> None:
        """Initialize the Google API client with credentials"""
        try:
            if not os.path.exists(self.config.credentials_path):
                raise GoogleClientError(f"Credentials file not found at {self.config.credentials_path}")

            self._credentials = service_account.Credentials.from_service_account_file(
                self.config.credentials_path,
                scopes=self.config.scopes
            )

            self._service = build(
                self.config.service_name,
                self.config.api_version,
                credentials=self._credentials,
                cache_discovery=False
            )
            logger.info(f"Successfully initialized {self.config.service_name} client")

        except Exception as e:
            logger.error(f"Failed to initialize Google client: {str(e)}")
            raise GoogleClientError(f"Client initialization failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda retry_state: None
    )
    async def execute_request(self, method: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a Google API request with retry mechanism.
        
        Args:
            method (str): The API method to call
            **kwargs: Additional arguments for the API call
            
        Returns:
            Dict[str, Any]: The API response
            
        Raises:
            GoogleClientError: If the request fails after all retries
        """
        try:
            service_method = self._resolve_method_path(method)
            response = service_method(**kwargs).execute()
            logger.info(f"Successfully executed {method}")
            return response

        except HttpError as e:
            logger.error(f"Google API error: {str(e)}")
            raise GoogleClientError(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise GoogleClientError(f"Unexpected error occurred: {str(e)}")

    def _resolve_method_path(self, method_path: str):
        """
        Resolve the API method from a dot-notation string.
        
        Args:
            method_path (str): Dot-notation method path (e.g., 'files.list')
            
        Returns:
            The resolved method
        """
        current = self._service
        for part in method_path.split('.'):
            current = getattr(current, part)
        return current

    @property
    def service(self):
        """Get the underlying Google service client"""
        return self._service

    def health_check(self) -> bool:
        """
        Perform a health check of the Google client
        
        Returns:
            bool: True if the client is healthy, False otherwise
        """
        try:
            if self._service and self._credentials and not self._credentials.expired:
                return True
            return False
        except Exception:
            return False

    def __enter__(self):
        """Context manager enter method"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method"""
        if self._service:
            self._service.close()

def create_google_client(
    credentials_path: str,
    scopes: list[str],
    service_name: str,
    api_version: str
) -> GoogleClient:
    """
    Factory function to create a new Google client instance.
    
    Args:
        credentials_path (str): Path to the credentials JSON file
        scopes (list[str]): List of required API scopes
        service_name (str): Name of the Google service
        api_version (str): API version to use
        
    Returns:
        GoogleClient: A new instance of the Google client
    """
    config = GoogleServiceConfig(
        credentials_path=credentials_path,
        scopes=scopes,
        service_name=service_name,
        api_version=api_version
    )
    return GoogleClient(config)