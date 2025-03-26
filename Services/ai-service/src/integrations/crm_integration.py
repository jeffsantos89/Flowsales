import requests
import os
from typing import Dict, Any
from enum import Enum
from requests.exceptions import RequestException
import logging
from retry import retry
from abc import ABC, abstractmethod

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRMProvider(Enum):
    HUBSPOT = "hubspot"
    SALESFORCE = "salesforce"
    RDSTATION = "rdstation"

class CRMServiceConfig:
    def __init__(self):
        self.CRM_SERVICE_URL = os.getenv("CRM_SERVICE_URL", "http://crm-service:8000")
        self.APIS = {
            CRMProvider.HUBSPOT.value: os.getenv("HUBSPOT_API_URL"),
            CRMProvider.SALESFORCE.value: os.getenv("SALESFORCE_API_URL"),
            CRMProvider.RDSTATION.value: os.getenv("RDSTATION_API_URL")
        }
        self.TIMEOUT = int(os.getenv("CRM_REQUEST_TIMEOUT", "30"))

class CRMIntegrationError(Exception):
    """Exceção customizada para erros de integração com CRM"""
    pass

class CRMInterface(ABC):
    @abstractmethod
    def add_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class CRMIntegration:
    def __init__(self):
        self.config = CRMServiceConfig()
        self.session = requests.Session()
    
    @retry(RequestException, tries=3, delay=1, backoff=2)
    def add_lead(self, crm: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona um lead ao CRM especificado através do crm-service
        
        Args:
            crm: Nome do CRM (deve ser um dos valores em CRMProvider)
            lead_data: Dicionário contendo os dados do lead
            
        Returns:
            Dict contendo a resposta do CRM
            
        Raises:
            CRMIntegrationError: Se houver erro na integração
            ValueError: Se o CRM não for suportado
        """
        try:
            if crm not in [provider.value for provider in CRMProvider]:
                raise ValueError(f"CRM '{crm}' não suportado")

            logger.info(f"Iniciando adição de lead no {crm}")
            
            # Integração com o crm-service
            url = f"{self.config.CRM_SERVICE_URL}/api/v1/leads/{crm}"
            
            headers = {
                "Content-Type": "application/json",
                "X-Request-ID": lead_data.get("request_id", ""),
                "X-Source-System": "ai-service"
            }
            
            response = self.session.post(
                url,
                json=lead_data,
                headers=headers,
                timeout=self.config.TIMEOUT
            )
            
            response.raise_for_status()
            
            logger.info(f"Lead adicionado com sucesso no {crm}")
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP ao adicionar lead: {str(e)}")
            raise CRMIntegrationError(f"Erro na integração com {crm}: {str(e)}")
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição ao CRM")
            raise CRMIntegrationError("Timeout na requisição ao CRM")
            
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise CRMIntegrationError(f"Erro inesperado: {str(e)}")

    def health_check(self) -> bool:
        """Verifica se o serviço está saudável"""
        try:
            response = self.session.get(f"{self.config.CRM_SERVICE_URL}/health")
            return response.status_code == 200
        except:
            return False

# Instância singleton
crm_integration = CRMIntegration()
