import pytest
from services.event_service import process_event
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import logging
import uuid
import json
from typing import Dict, Any
import time
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]
KAFKA_TOPIC = "test_topic"
CONSUMER_TIMEOUT_MS = 10000
MAX_RETRIES = 3
RETRY_DELAY = 1

@contextmanager
def kafka_resources():
    """Context manager for Kafka resources to ensure proper cleanup"""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries=MAX_RETRIES,
        retry_backoff_ms=1000
    )
    
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        consumer_timeout_ms=CONSUMER_TIMEOUT_MS,
        group_id=f'test-group-{uuid.uuid4()}'
    )

    try:
        yield producer, consumer
    finally:
        producer.close()
        consumer.close()

def send_message(producer: KafkaProducer, message: Dict[str, Any]) -> bool:
    """Send message to Kafka with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            future = producer.send(KAFKA_TOPIC, message)
            future.get(timeout=10)  # Wait for message to be delivered
            logger.info(f"Message sent successfully: {message}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return False

@pytest.fixture(scope="module")
def kafka_fixture():
    with kafka_resources() as resources:
        yield resources

def test_kafka_event(kafka_fixture):
    """Test Kafka event processing with proper message structure and validation"""
    producer, consumer = kafka_fixture
    
    # Prepare test message
    test_message = {
        "id": str(uuid.uuid4()),
        "timestamp": int(time.time() * 1000),
        "type": "test_event",
        "payload": {
            "data": "Test Message",
            "version": "1.0"
        }
    }

    # Send message
    assert send_message(producer, test_message)

    # Verify message reception
    received = False
    start_time = time.time()
    
    while time.time() - start_time < CONSUMER_TIMEOUT_MS/1000:
        msg = next(consumer, None)
        if msg:
            received_message = msg.value
            assert received_message["id"] == test_message["id"]
            assert received_message["type"] == test_message["type"]
            assert received_message["payload"]["data"] == test_message["payload"]["data"]
            received = True
            break

    assert received, "Message was not received within the timeout period"
