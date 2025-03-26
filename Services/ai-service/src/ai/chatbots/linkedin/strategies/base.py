"""
base.py
Definição de classe base para estratégias específicas do LinkedIn.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLinkedInStrategy(ABC):
    """
    Classe base para estratégias de interação do LinkedIn (conexão, prospecção, mensagens, etc.).
    """

    @abstractmethod
    def execute(self, user_id: str, message_text: str, conversation: Dict[str, Any], query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a lógica específica da estratégia.

        Args:
            user_id (str): ID do usuário no LinkedIn
            message_text (str): Texto cru da mensagem
            conversation (dict): Estado atual da conversa (ex.: 'state', 'messages')
            query_info (dict): Resultados da pipeline NLP (intenção, entidades, etc.)

        Returns:
            dict: Resposta estruturada contendo o que deve ser enviado ao usuário.
        """
        pass
        @abstractmethod
        def validate(self, **kwargs) -> bool:
            """
            Valida se a estratégia pode ser executada com os parâmetros fornecidos.

            Args:
                **kwargs: Argumentos variáveis para validação

            Returns:
                bool: True se a estratégia pode ser executada, False caso contrário
            """
            pass

        @abstractmethod
        def pre_execute_hooks(self, **kwargs) -> None:
            """
            Executa ações necessárias antes da execução principal.
            """
            pass

        @abstractmethod
        def post_execute_hooks(self, **kwargs) -> None:
            """
            Executa ações necessárias após a execução principal.
            """
            pass

        def handle_error(self, error: Exception) -> Dict[str, Any]:
            """
            Trata erros que ocorrem durante a execução da estratégia.

            Args:
                error (Exception): Erro capturado

            Returns:
                dict: Resposta de erro estruturada
            """
            return {
                "success": False,
                "error": str(error),
                "error_type": error.__class__.__name__
            }