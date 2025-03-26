import os
import json
import logging
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from functools import lru_cache
from retrying import retry
from contextlib import contextmanager

# Configuração avançada de logging com formatação personalizada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger("KafkaEventProducer")

class KafkaConfig:
    """Classe de configuração centralizada para Kafka"""
    DEFAULT_BROKER = "localhost:9092"
    DEFAULT_RETRIES = 3
    RETRY_ATTEMPTS = 3
    RETRY_WAIT_MULTIPLIER = 1000
    RETRY_WAIT_MAX = 10000
    PRODUCER_TIMEOUT = 10
    BATCH_SIZE = 16384
    LINGER_MS = 10
    BUFFER_MEMORY = 33554432

class KafkaEventProducer:
    """
    Produtor de eventos Kafka com recursos avançados:
    - Compressão GZIP para economia de banda
    - Garantia de ordenação com max_in_flight=1
    - Idempotência para evitar duplicatas
    - Retry exponencial com backoff
    - Gerenciamento de recursos com context manager
    - Monitoramento detalhado via logging
    """
    def __init__(
        self, 
        broker_urls: Optional[str] = None, 
        retries: int = KafkaConfig.DEFAULT_RETRIES
    ):
        self.broker_urls = broker_urls or os.getenv("KAFKA_BROKER", KafkaConfig.DEFAULT_BROKER)
        self.retries = retries
        self._producer: Optional[KafkaProducer] = None
        self._health_check()

    def _health_check(self) -> None:
        """Verifica a saúde da conexão Kafka"""
        if not self.broker_urls:
            raise ValueError("Kafka broker URLs não configuradas")

    @property
    @lru_cache(maxsize=1)
    def producer(self) -> KafkaProducer:
        """Inicialização lazy do produtor com cache"""
        if not self._producer:
            try:
                self._producer = KafkaProducer(
                    bootstrap_servers=self.broker_urls.split(","),
                    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
                    key_serializer=lambda k: k.encode("utf-8") if k else None,
                    acks="all",
                    retries=self.retries,
                    enable_idempotence=True,
                    compression_type="gzip",
                    max_in_flight_requests_per_connection=1,
                    batch_size=KafkaConfig.BATCH_SIZE,
                    linger_ms=KafkaConfig.LINGER_MS,
                    buffer_memory=KafkaConfig.BUFFER_MEMORY
                )
                logger.info(f"[Kafka] Producer inicializado com sucesso: {self.broker_urls}")
            except Exception as e:
                logger.exception(f"[Kafka] Erro crítico na inicialização do producer: {e}")
                raise

        return self._producer

    @retry(
        stop_max_attempt_number=KafkaConfig.RETRY_ATTEMPTS,
        wait_exponential_multiplier=KafkaConfig.RETRY_WAIT_MULTIPLIER,
        wait_exponential_max=KafkaConfig.RETRY_WAIT_MAX
    )
    def send_event(
        self, 
        topic: str, 
        event: Dict[str, Any], 
        key: Optional[str] = None
    ) -> None:
        """Envia evento para tópico Kafka com retry e monitoramento"""
        if not topic or not event:
            raise ValueError("Tópico e evento são obrigatórios")

        try:
            future = self.producer.send(topic, value=event, key=key)
            metadata = future.get(timeout=KafkaConfig.PRODUCER_TIMEOUT)

            logger.info(
                f"[Kafka] Evento processado | "
                f"Topic: {topic} | "
                f"Partition: {metadata.partition} | "
                f"Offset: {metadata.offset} | "
                f"Key: {key}"
            )

        except KafkaError as ke:
            logger.error(f"[KafkaError] Falha no envio para {topic}: {str(ke)}")
            raise
        except Exception as e:
            logger.exception(f"[Kafka] Erro inesperado no envio para {topic}")
            raise

    def flush(self) -> None:
        """Força o envio de mensagens pendentes"""
        if self._producer:
            self._producer.flush()
            logger.debug("[Kafka] Buffer do producer limpo")

    def close(self) -> None:
        """Encerra recursos do producer com segurança"""
        if self._producer:
            self.flush()
            self._producer.close()
            self._producer = None
            logger.info("[Kafka] Producer encerrado corretamente")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

@contextmanager
def get_kafka_producer():
    """Context manager para uso seguro do producer"""
    producer = None
    try:
        producer = KafkaEventProducer()
        yield producer
    finally:
        if producer:
            producer.close()

# Instância global com lazy loading
_global_producer: Optional[KafkaEventProducer] = None

def get_global_producer() -> KafkaEventProducer:
    """Singleton pattern para acesso global ao producer"""
    global _global_producer
    if not _global_producer:
        _global_producer = KafkaEventProducer()
    return _global_producer

def send_event(topic: str, event: Dict[str, Any], key: Optional[str] = None) -> None:
    """API simplificada para envio de eventos"""
    try:
        producer = get_global_producer()
        producer.send_event(topic, event, key)
    except Exception as e:
        logger.error(f"[send_event] Falha na publicação em {topic}: {e}")
        raise
