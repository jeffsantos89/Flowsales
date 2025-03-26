# src/ai/queue/kafka_backend.py
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import Dict, Optional, AsyncGenerator
import json
import logging
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)

@dataclass
class KafkaConfig:
    bootstrap_servers: str
    topic: str
    client_id: str
    group_id: str
    security_protocol: str = "PLAINTEXT"
    ssl_cafile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None

def retry_on_exception(retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{retries} failed: {str(e)}")
                    if attempt < retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator

class KafkaQueueBackend:
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._connected = False

    async def _create_producer(self) -> AIOKafkaProducer:
        return AIOKafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            client_id=f"{self.config.client_id}-producer",
            security_protocol=self.config.security_protocol,
            ssl_cafile=self.config.ssl_cafile,
            ssl_certfile=self.config.ssl_certfile,
            ssl_keyfile=self.config.ssl_keyfile,
            retry_backoff_ms=500,
            enable_idempotence=True
        )

    async def _create_consumer(self) -> AIOKafkaConsumer:
        return AIOKafkaConsumer(
            self.config.topic,
            bootstrap_servers=self.config.bootstrap_servers,
            client_id=f"{self.config.client_id}-consumer",
            group_id=self.config.group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            security_protocol=self.config.security_protocol,
            ssl_cafile=self.config.ssl_cafile,
            ssl_certfile=self.config.ssl_certfile,
            ssl_keyfile=self.config.ssl_keyfile
        )

    @asynccontextmanager
    async def connection(self):
        try:
            await self.connect()
            yield self
        finally:
            await self.close()

    async def connect(self):
        if self._connected:
            return

        try:
            self.producer = await self._create_producer()
            await self.producer.start()
            self.consumer = await self._create_consumer()
            await self.consumer.start()
            self._connected = True
            logger.info("Successfully connected to Kafka")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            await self.close()
            raise

    async def close(self):
        if self.producer:
            await self.producer.stop()
            self.producer = None
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None
        self._connected = False
        logger.info("Kafka connections closed")

    @retry_on_exception(retries=3)
    async def send(self, message: Dict) -> None:
        if not self._connected:
            await self.connect()
        
        try:
            message_bytes = json.dumps(message).encode("utf-8")
            await self.producer.send_and_wait(
                self.config.topic,
                message_bytes,
                partition=None  # You can implement custom partitioning logic here
            )
            logger.debug(f"Message sent successfully to topic {self.config.topic}")
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise

    async def receive(self) -> AsyncGenerator[Dict, None]:
        if not self._connected:
            await self.connect()

        try:
            async for msg in self.consumer:
                try:
                    yield json.loads(msg.value)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Error in consumer: {str(e)}")
            await self.close()
            raise

