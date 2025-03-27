"""
Client module initialization.
This module provides centralized access to various API clients.
"""

from typing import TYPE_CHECKING

# Lazy imports to avoid circular dependencies
if TYPE_CHECKING:
    from auth_client import AuthClient
    from crm_client import CRMClient

__all__ = ['AuthClient', 'CRMClient']

# Expose the client classes through lazy loading
def get_auth_client() -> 'AuthClient':
    from auth_client import AuthClient
    return AuthClient

def get_crm_client() -> 'CRMClient':
    from crm_client import CRMClient
    return CRMClient
from src.clients import (
    AuthClient,
    CRMClient,
    LeadsClient,
    WhatsAppClient,
    MarketplaceClient,
)
from src.clients.auth_client import AuthClient
from src.clients.crm_client import CRMClient