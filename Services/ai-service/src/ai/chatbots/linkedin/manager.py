"""
manager.py
Responsável por orquestrar eventos do LinkedIn, como webhooks, endpoints REST,
ou job schedulers que chamam o bot e gerenciam estados globais.
"""

import logging
import asyncio
import signal
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import traceback
from contextlib import asynccontextmanager

from linkedin.linkedinBot import LinkedInBot
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@dataclass
class BotMetrics:
    """Métricas do bot para monitoramento"""
    total_messages: int = 0
    successful_responses: int = 0
    failed_responses: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None

class LinkedInBotManagerError(Exception):
    """Exceção base para erros do LinkedInBotManager"""
    pass

class LinkedInBotManager:
    """
    Classe que gerencia o ciclo de vida do LinkedInBot: start, stop,
    processa mensagens de webhook ou fila, etc.
    """
    def __init__(self, linkedin_bot: LinkedInBot, max_concurrent_tasks: int = 100):
        self.bot = linkedin_bot
        self._running = False
        self.metrics = BotMetrics()
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._tasks: set[asyncio.Task] = set()
        self._startup_time = None
        self._shutdown_hook_registered = False

    @asynccontextmanager
    async def managed_task(self):
        """Context manager para gerenciar tasks de forma segura"""
        try:
            yield
        except Exception as e:
            self.metrics.failed_responses += 1
            self.metrics.last_error = str(e)
            self.metrics.last_error_time = datetime.utcnow()
            logger.error(f"Erro na task: {e}\n{traceback.format_exc()}")
            raise
        finally:
            self.metrics.total_messages += 1

    async def start(self):
        """
        Inicia a execução do Manager, preparando recursos assíncronos se necessário.
        """
        if self._running:
            raise LinkedInBotManagerError("Manager já está rodando")

        try:
            await self.bot.initialize()  # Método hipotético para inicialização do bot
            self._running = True
            self._startup_time = datetime.utcnow()
            
            if not self._shutdown_hook_registered:
                asyncio.get_event_loop().add_signal_handler(
                    signal.SIGTERM, 
                    lambda: asyncio.create_task(self.stop())
                )
                self._shutdown_hook_registered = True
                
            logger.info("[LinkedInBotManager] Iniciado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao iniciar manager: {e}")
            raise LinkedInBotManagerError(f"Falha na inicialização: {e}")

    async def stop(self):
        """
        Finaliza recursos (conexões, filas, etc.) antes de encerrar.
        """
        if not self._running:
            return

        logger.info("[LinkedInBotManager] Iniciando shutdown...")
        self._running = False

        # Cancela todas as tasks pendentes
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        await self.bot.cleanup()  # Método hipotético para limpeza do bot
        
        logger.info("[LinkedInBotManager] Parado com sucesso.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_incoming(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Método assíncrono para processar uma mensagem recebida do LinkedIn,
        chamando o `LinkedInBot`.
        """
        if not self._running:
            raise LinkedInBotManagerError("LinkedInBotManager não está rodando")

        async with self._semaphore, self.managed_task():
            logger.debug(f"[Manager] Processando mensagem de user_id={user_id}: {message}")
            
            task = asyncio.create_task(
                self._process_message(user_id, message)
            )
            self._tasks.add(task)
            try:
                result = await task
                self.metrics.successful_responses += 1
                return result
            finally:
                self._tasks.remove(task)

    async def _process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Processa a mensagem em uma thread separada"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.bot.handle_incoming_message,
            user_id,
            message
        )

    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna status detalhado do manager/bot
        """
        uptime = (datetime.utcnow() - self._startup_time).total_seconds() if self._startup_time else 0
        
        return {
            "running": self._running,
            "active_sessions": len(self.bot.conversations),
            "uptime_seconds": uptime,
            "metrics": {
                "total_messages": self.metrics.total_messages,
                "successful_responses": self.metrics.successful_responses,
                "failed_responses": self.metrics.failed_responses,
                "success_rate": (
                    self.metrics.successful_responses / self.metrics.total_messages * 100
                    if self.metrics.total_messages > 0 else 0
                ),
                "last_error": self.metrics.last_error,
                "last_error_time": self.metrics.last_error_time,
            },
            "current_load": len(self._tasks),
        }
