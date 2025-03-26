# src/events/kafka_producer.py
from kafka import KafkaProducer, KafkaError
import json
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaProducerService:
    def __init__(self, bootstrap_servers: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=5,  # Retry up to 5 times
            acks='all'  # Wait for all replicas to acknowledge
        )

    def send_event(self, topic: str, message: Dict):
        try:
            future = self.producer.send(topic, message)
            result = future.get(timeout=10)  # Block for 'synchronous' sends
            logger.info(f"Message sent to {result.topic} partition {result.partition} at offset {result.offset}")
        except KafkaError as e:
            logger.error(f"Failed to send message: {e}")
            # Handle the error appropriately
        finally:
            self.producer.flush()

    def close(self):
        self.producer.close()

# Usage example
if __name__ == "__main__":
    kafka_service = KafkaProducerService(bootstrap_servers="localhost:9092")
    try:
        kafka_service.send_event("my_topic", {"key": "value"})
    finally:
        kafka_service.close()
# Caminho: src/ai/events/kafka_producer.py

import json
import logging
from typing import Dict, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from functools import lru_cache
from types import SimpleNamespace
from unittest.mock import patch

logger = logging.getLogger("KafkaProducerService")

class KafkaProducerService:
    """
    Serviço de envio de mensagens para Kafka com segurança, observabilidade e idempotência.
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092", enable_compression: bool = True):
        self.bootstrap_servers = bootstrap_servers
        self._producer: Optional[KafkaProducer] = None
        self.enable_compression = enable_compression

    @property
    @lru_cache(maxsize=1)
    def producer(self) -> KafkaProducer:
        try:
            if not self._producer:
                self._producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers.split(","),
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    acks="all",
                    retries=5,
                    enable_idempotence=True,
                    max_in_flight_requests_per_connection=1,
                    compression_type="gzip" if self.enable_compression else None,
                    linger_ms=5
                )
                logger.info(f"[Kafka] Producer conectado: {self.bootstrap_servers}")
            return self._producer
        except Exception as e:
            logger.exception("[Kafka] Erro ao criar KafkaProducer")
            raise

    def send_event(self, topic: str, message: Dict, key: Optional[str] = None):
        try:
            future = self.producer.send(
                topic=topic,
                value=message,
                key=key.encode() if key else None
            )
            metadata = future.get(timeout=10)
            logger.info(
                f"[Kafka] Mensagem enviada: topic={metadata.topic}, "
                f"partition={metadata.partition}, offset={metadata.offset}"
            )
        except KafkaError as ke:
            logger.error(f"[KafkaError] Falha ao enviar: {ke}")
            raise
        except Exception as e:
            logger.exception(f"[Kafka] Erro inesperado ao enviar para {topic}")
            raise

    def close(self):
        if self._producer:
            self._producer.flush()
            self._producer.close()
            logger.info("[Kafka] Producer encerrado com sucesso")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
        # Unit tests
        def test_kafka_producer():
            producer = KafkaProducerService("test-server:9092")
            try:
                # Mock testing example
                with patch('kafka.KafkaProducer') as mock_producer:
                    mock_producer.return_value.send.return_value.get.return_value = \
                        SimpleNamespace(topic='test', partition=0, offset=1)
                    
                    producer.send_event("test-topic", {"test": "data"}, "test-key")
                    
                    mock_producer.assert_called_once()
            finally:
                producer.close()

        if __name__ == "__main__":
            # Example usage with context manager
            with KafkaProducerService(
                bootstrap_servers="localhost:9092",
                enable_compression=True
            ) as producer:
                producer.send_event(
                    topic="test-topic",
                    message={"key": "value"},
                    key="message-key"
                )