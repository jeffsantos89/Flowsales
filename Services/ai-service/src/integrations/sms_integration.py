from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
import logging
from typing import Optional, Dict
from dataclasses import dataclass
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TwilioConfig:
    """Classe para armazenar configurações do Twilio"""
    account_sid: str
    auth_token: str
    phone_number: str

class SMSService:
    """Serviço para envio de SMS usando Twilio"""
    
    def __init__(self):
        self.config = self._load_config()
        self.client = Client(self.config.account_sid, self.config.auth_token)

    def _load_config(self) -> TwilioConfig:
        """Carrega e valida as configurações do Twilio"""
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        phone_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not all([account_sid, auth_token, phone_number]):
            raise ValueError("Todas as variáveis de ambiente do Twilio são necessárias")

        return TwilioConfig(account_sid, auth_token, phone_number)

    @staticmethod
    def _validate_phone_number(phone: str) -> bool:
        """Valida o formato do número de telefone"""
        phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        return bool(phone_pattern.match(phone))

    @staticmethod
    def _validate_message(message: str) -> bool:
        """Valida o conteúdo da mensagem"""
        return bool(message and len(message.strip()) <= 1600)

    def send_sms(self, recipient: str, message: str) -> Dict[str, str]:
        """
        Envia um SMS usando Twilio
        
        Args:
            recipient: Número do destinatário
            message: Conteúdo da mensagem

        Returns:
            Dict contendo status e informações da mensagem

        Raises:
            ValueError: Se os parâmetros forem inválidos
            TwilioRestException: Se houver erro no envio
        """
        try:
            # Validações
            if not self._validate_phone_number(recipient):
                raise ValueError("Número de telefone inválido")
            
            if not self._validate_message(message):
                raise ValueError("Mensagem inválida ou muito longa")

            # Envio da mensagem
            logger.info(f"Enviando SMS para {recipient}")
            response = self.client.messages.create(
                body=message,
                from_=self.config.phone_number,
                to=recipient
            )

            logger.info(f"SMS enviado com sucesso. SID: {response.sid}")
            return {
                "status": "success",
                "message_sid": response.sid,
                "to": recipient,
                "message": message
            }

        except TwilioRestException as e:
            logger.error(f"Erro
