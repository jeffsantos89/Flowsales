import json
import logging
import os
from typing import Dict, Any, Callable, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps
import signal
import time
from prometheus_client import Counter, Histogram, start_http_server

# Métricas Prometheus
EVENTS_PROCESSED = Counter('events_processed_total', 'Total de eventos processados', ['event_type'])
PROCESSING_TIME = Histogram('event_processing_seconds', 'Tempo de processamento de eventos')
ERROR_COUNT = Counter('event_processing_errors_total', 'Total de erros no processamento')

# Configuração de logging avançada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('event_processor.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class KafkaConfig:
    """Configurações imutáveis do Kafka"""
    broker: str = os.getenv("KAFKA_BROKER", "localhost:9092")
    topic: str = os.getenv("KAFKA_TOPIC", "ai_predictions")
    group_id: str = os.getenv("KAFKA_GROUP", "ai_prediction_consumer_group")
    auto_offset_reset: str = "earliest"
    max_poll_records: int = int(os.getenv("KAFKA_MAX_POLL_RECORDS", "100"))
    max_workers: int = int(os.getenv("KAFKA_MAX_WORKERS", "5"))
    consumer_timeout_ms: int = int(os.getenv("KAFKA_CONSUMER_TIMEOUT_MS", "1000"))
    metrics_port: int = int(os.getenv("METRICS_PORT", "8000"))

def retry_on_error(retries: int = 3, delay: float = 1.0):
    """Decorator para retry em caso de falhas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Tentativa {attempt + 1}/{retries} falhou: {e}")
                    if attempt < retries - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator

class EventProcessor:
    """Processador de eventos do Kafka com recursos avançados"""
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.consumer = None
        self.executor = None
        self.running = False
        self.event_handlers = {}
        self._setup_metrics_server()
        self._setup_signal_handlers()
        
    def _setup_metrics_server(self):
        """Inicializa servidor de métricas Prometheus"""
        start_http_server(self.config.metrics_port)
        logger.info(f"Servidor de métricas iniciado na porta {self.config.metrics_port}")

    def _setup_signal_handlers(self):
        """Configura handlers para sinais do sistema"""
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handler para shutdown gracioso"""
        logger.info(f"Recebido sinal {signum}. Iniciando shutdown...")
        self.running = False

    @retry_on_error(retries=3)
    def _create_consumer(self) -> KafkaConsumer:
        """Cria e configura o consumidor Kafka com retry"""
        logger.info(f"Conectando ao Kafka em {self.config.broker}")
        return KafkaConsumer(
            self.config.topic,
            bootstrap_servers=self.config.broker,
            group_id=self.config.group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset=self.config.auto_offset_reset,
            max_poll_records=self.config.max_poll_records,
            enable_auto_commit=True,
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000
        )

    def register_handler(self, event_type: str, handler: Callable):
        """Registra handlers para diferentes tipos de eventos"""
        self.event_handlers[event_type.lower()] = handler

    @PROCESSING_TIME.time()
    def process_event(self, event: Dict[str, Any]) -> None:
        """Processa eventos com métricas e tratamento de erros"""
        try:
            event_type = event.get("type", "").lower()
            handler = self.event_handlers.get(event_type)
            
            if handler:
                logger.debug(f"Processando evento: {event_type}")
                handler(event)
                EVENTS_PROCESSED.labels(event_type=event_type).inc()
            else:
                logger.warning(f"Handler não encontrado para evento: {event_type}")
        except Exception as e:
            ERROR_COUNT.inc()
            logger.error(f"Erro no processamento: {e}", exc_info=True)
            raise

    @contextmanager
    def consumer_context(self):
        """Gerenciador de contexto para recursos"""
        try:
            self.consumer = self._create_consumer()
            self.executor = ThreadPoolExecutor(
                max_workers=self.config.max_workers,
                thread_name_prefix="EventProcessor"
            )
            self.running = True
            yield
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Realiza shutdown controlado"""
        logger.info("Iniciando processo de shutdown...")
        self.running = False
        
        if self.executor:
            logger.info("Encerrando executor...")
            self.executor.shutdown(wait=True)
        
        if self.consumer:
            logger.info("Fechando consumidor Kafka...")
            self.consumer.close()

    def consume_events(self) -> None:
        """Loop principal de consumo com controle de execução"""
        with self.consumer_context():
            logger.info("Iniciando consumo de eventos")
            while self.running:
                try:
                    messages = self.consumer.poll(
                        timeout_ms=self.config.consumer_timeout_ms
                    )
                    for topic_partition, partition_messages in messages.items():
                        for message in partition_messages:
                            self.executor.submit(self.process_event, message.value)
                except Exception as e:
                    logger.error(f"Erro no consumo: {e}", exc_info=True)
                    if self.running:  # Só tenta reconectar se ainda estiver rodando
                        time.sleep(1)
                        self.consumer = self._create_consumer()

def main():
    """Função principal com setup completo"""
    try:
        config = KafkaConfig()
        processor = EventProcessor(config)
        
        # Registra handlers para diferentes tipos de eventos
        processor.register_handler("prediction_made", 
                                 lambda event: logger.info(f"Previsão processada: {event}"))
        
        logger.info("Iniciando processador de eventos...")
        processor.consume_events()
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
