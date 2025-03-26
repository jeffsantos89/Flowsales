import pytest
import json
from unittest.mock import Mock, patch
from confluent_kafka import Producer, Consumer
import asyncio
from datetime import datetime
from typing import Dict, Any

class TestKafkaEvents:
    @pytest.fixture(scope="class")
    def kafka_config(self) -> Dict[str]:
        return {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'test_consumer_group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }

    @pytest.fixture(scope="function")
    async def kafka_producer(self) -> Producer:
        producer_config = {'bootstrap.servers': 'localhost:9092'}
        producer = Producer(producer_config)
        yield producer
        producer.flush()

    @pytest.fixture(scope="function")
    async def kafka_consumer(self, kafka_config) -> Consumer:
        consumer = Consumer(kafka_config)
        yield consumer
        consumer.close()

    @pytest.mark.asyncio
    async def test_message_production_and_consumption(self, kafka_producer, kafka_consumer):
        test_topic = "test_topic"
        test_message = {
            "id": "123",
            "event_type": "test_event",
            "timestamp": datetime.now().isoformat(),
            "data": {"key": "value"}
        }

        # Produce message
        try:
            kafka_producer.produce(
                topic=test_topic,
                value=json.dumps(test_message).encode('utf-8'),
                callback=self._delivery_report
            )
            kafka_producer.flush()

            # Subscribe and consume
            kafka_consumer.subscribe([test_topic])
            message = await self._consume_message(kafka_consumer)

            # Assertions
            assert message is not None
            consumed_data = json.loads(message.value().decode('utf-8'))
            assert consumed_data["id"] == test_message["id"]
            assert consumed_data["event_type"] == test_message["event_type"]

        except Exception as e:
            pytest.fail(f"Test failed with exception: {str(e)}")

    @pytest.mark.asyncio
    async def test_message_schema_validation(self, kafka_producer):
        test_topic = "test_topic"
        invalid_message = {
            "invalid_field": "test"  # Missing required fields
        }

        with pytest.raises(Exception):
            kafka_producer.produce(
                topic=test_topic,
                value=json.dumps(invalid_message).encode('utf-8'),
                callback=self._delivery_report
            )

    @pytest.mark.asyncio
    async def test_multiple_messages_ordering(self, kafka_producer, kafka_consumer):
        test_topic = "test_topic"
        messages = [
            {"id": str(i), "sequence": i, "data": f"test_{i}"} 
            for i in range(5)
        ]

        # Produce multiple messages
        for msg in messages:
            kafka_producer.produce(
                topic=test_topic,
                value=json.dumps(msg).encode('utf-8'),
                callback=self._delivery_report
            )
        kafka_producer.flush()

        # Consume and verify ordering
        kafka_consumer.subscribe([test_topic])
        consumed_messages = []
        for _ in range(len(messages)):
            message = await self._consume_message(kafka_consumer)
            if message:
                consumed_messages.append(
                    json.loads(message.value().decode('utf-8'))
                )

        # Verify sequence
        sequences = [msg["sequence"] for msg in consumed_messages]
        assert sequences == sorted(sequences)

    @staticmethod
    def _delivery_report(err, msg):
        if err is not None:
            pytest.fail(f'Message delivery failed: {err}')

    @staticmethod
    async def _consume_message(consumer: Consumer, timeout: float = 5.0) -> Any:
        """Helper method to consume a single message with timeout"""
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            msg = consumer.poll(1.0)
            if msg is not None:
                return msg
            await asyncio.sleep(0.1)
        return None

    def teardown_method(self, method):
        """Cleanup after each test method"""
        # Additional cleanup if needed
        pass

    @classmethod
    def teardown_class(cls):
        """Cleanup after the test class"""
        # Additional cleanup if needed
        pass