import psutil
import os
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import platform

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict
    process_count: int

class SystemMonitor:
    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self._last_metrics: Optional[SystemMetrics] = None

    def get_system_metrics(self) -> SystemMetrics:
        """
        Coleta métricas detalhadas do sistema de forma thread-safe.
        """
        try:
            with ThreadPoolExecutor(max_workers=4) as executor:
                cpu_future = executor.submit(psutil.cpu_percent, self.sampling_interval)
                memory_future = executor.submit(lambda: psutil.virtual_memory().percent)
                disk_future = executor.submit(lambda: psutil.disk_usage('/').percent)
                network_future = executor.submit(psutil.net_io_counters)

            metrics = SystemMetrics(
                cpu_usage=cpu_future.result(),
                memory_usage=memory_future.result(),
                disk_usage=disk_future.result(),
                network_io={
                    'bytes_sent': network_future.result().bytes_sent,
                    'bytes_recv': network_future.result().bytes_recv
                },
                process_count=len(psutil.pids())
            )
            
            self._last_metrics = metrics
            return metrics

        except Exception as e:
            logger.error(f"Erro ao coletar métricas: {str(e)}")
            raise

class ProcessManager:
    @staticmethod
    def set_process_priority(nice_value: int = -10) -> bool:
        """
        Ajusta a prioridade do processo atual com tratamento específico por sistema operacional.
        """
        try:
            system = platform.system().lower()
            
            if system == 'linux':
                os.nice(nice_value)
                logger.info(f"Prioridade ajustada em Linux: {nice_value}")
            elif system == 'windows':
                import win32process
                import win32con
                import win32api
                
                pid = os.getpid()
                handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
                win32process.SetPriorityClass(handle, win32con.HIGH_PRIORITY_CLASS)
                logger.info("Prioridade ajustada em Windows: HIGH_PRIORITY_CLASS")
                pid = os.getpid()
                handle = win32api.OpenProcess(win32process.PROCESS_ALL_ACCESS, True, pid)
                win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
                logger.info("Prioridade ajustada em Windows: HIGH_PRIORITY_CLASS")
            else:
                logger.warning(f"Sistema operacional não suportado: {system}")
                return False
                
            return True

        except Exception as e:
            logger.error(f"Erro ao ajustar prioridade: {str(e)}")
            return False

def main():
    monitor = SystemMonitor(sampling_interval=1.0)
    process_manager = ProcessManager()

    try:
        # Configura prioridade do processo
        if process_manager.set_process_priority():
            logger.info("Prioridade do processo ajustada com sucesso")
        
        # Monitor contínuo
        while True:
            metrics = monitor.get_system_metrics()
            logger.info(f"Métricas do Sistema: {metrics}")
            sleep(5)  # Intervalo entre verificações

    except KeyboardInterrupt:
        logger.info("Monitoramento finalizado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
