import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)

# Kafka configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
DLQ_TOPIC = os.getenv('DLQ_TOPIC', 'dlq')

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_to_dlq(event):
    """Envia eventos com erro para Dead Letter Queue"""
    producer.send(DLQ_TOPIC, event)
    producer.flush()
    print(f"Evento enviado para DLQ: {event}")

consumer = KafkaConsumer(
    DLQ_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest'
)

def consume_dlq():
    """Consome eventos da Dead Letter Queue"""
    for message in consumer:
        print(f"Evento na DLQ: {message.value}")

# Caminho: src/ai/queue/kafka_dlq.py

import os
import json
import logging
from typing import Any, Dict, Generator

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("kafka_dlq")
logging.basicConfig(level=logging.INFO)

# Configurações
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
DLQ_TOPIC = os.getenv("DLQ_TOPIC", "dead-letter-queue")

# Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=3,
    acks="all"
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def send_to_dlq(event: Dict[str, Any]) -> None:
    """
    Envia um evento para o tópico de Dead Letter Queue.
    """
    try:
        future = producer.send(DLQ_TOPIC, event)
        result = future.get(timeout=10)
        logger.info(f"[DLQ] Evento enviado para DLQ: {result}")
    except KafkaError as e:
        logger.exception(f"[DLQ] Falha ao enviar evento: {event}")
        raise

# Consumer (somente leitura)
consumer = KafkaConsumer(
    DLQ_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="dlq-monitor"
)

def consume_dlq() -> Generator[Dict[str, Any], None, None]:
    """
    Gera eventos consumidos da DLQ.
    """
    for message in consumer:
        logger.warning(f"[DLQ] Evento recebido da DLQ: {message.value}")
        yield message.value
        class DeadLetterQueue:
            def __init__(
                self, 
                broker: str = KAFKA_BROKER,
                topic: str = DLQ_TOPIC,
                max_retries: int = 3,
                timeout: int = 10
            ):
                self._broker = broker
                self._topic = topic
                self._max_retries = max_retries
                self._timeout = timeout
                self._producer = self._create_producer()
                self._consumer = self._create_consumer()
                self._logger = logging.getLogger(__name__)

            def _create_producer(self) -> KafkaProducer:
                return KafkaProducer(
                    bootstrap_servers=self._broker,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    retries=self._max_retries,
                    acks="all",
                    compression_type="gzip",
                    batch_size=16384,
                    linger_ms=100
                )

            def _create_consumer(self) -> KafkaConsumer:
                return KafkaConsumer(
                    self._topic,
                    bootstrap_servers=self._broker,
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                    auto_offset_reset="earliest",
                    enable_auto_commit=False,
                    group_id="dlq-monitor",
                    fetch_max_bytes=52428800,
                    max_partition_fetch_bytes=1048576
                )

            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                reraise=True
            )
            async def send(self, event: Dict[str, Any], metadata: Dict[str, Any] = None) -> None:
                try:
                    enriched_event = {
                        "event": event,
                        "metadata": {
                            "timestamp": str(datetime.utcnow()),
                            "retry_count": 0,
                            **(metadata or {})
                        }
                    }
                    future = self._producer.send(self._topic, enriched_event)
                    result = future.get(timeout=self._timeout)
                    self._logger.info(f"Event sent to DLQ: {result}", extra={"event": enriched_event})
                except Exception as e:
                    self._logger.error(f"Failed to send event to DLQ: {str(e)}", 
                                     extra={"event": event, "error": str(e)})
                    raise

            async def process(self, handler: Callable[[Dict[str, Any]], Any]) -> None:
                try:
                    for message in self._consumer:
                        try:
                            await handler(message.value)
                            self._consumer.commit()
                        except Exception as e:
                            self._logger.error(f"Error processing DLQ message: {str(e)}", 
                                             extra={"message": message.value, "error": str(e)})
                finally:
                    self._consumer.close()
                    self._producer.close()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self._consumer.close()
                self._producer.close()