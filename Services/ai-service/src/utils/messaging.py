import json
import logging
from typing import Any, Dict, Optional
import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessagingService:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            self.channel = self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def close_connection(self):
        if self.connection:
            self.connection.close()
            logger.info("Connection to RabbitMQ closed")

    def declare_queue(self, queue_name: str, durable: bool = True):
        self.channel.queue_declare(queue=queue_name, durable=durable)
        logger.info(f"Queue declared: {queue_name}")

    def publish_message(self, queue_name: str, message: Dict[str, Any], persistent: bool = True):
        properties = pika.BasicProperties(delivery_mode=2) if persistent else None
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=properties
        )
        logger.info(f"Message published to {queue_name}: {message}")

    def consume_messages(self, queue_name: str, callback, auto_ack: bool = False):
        def wrapper(ch, method, properties, body):
            message = json.loads(body)
            callback(message)
            if not auto_ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=queue_name, on_message_callback=wrapper, auto_ack=auto_ack)
        logger.info(f"Started consuming messages from {queue_name}")
        self.channel.start_consuming()

    def setup_exchange(self, exchange_name: str, exchange_type: str = 'direct', durable: bool = True):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=durable)
        logger.info(f"Exchange declared: {exchange_name}")

    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str):
        self.channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)
        logger.info(f"Queue {queue_name} bound to exchange {exchange_name} with routing key {routing_key}")

    def publish_to_exchange(self, exchange_name: str, routing_key: str, message: Dict[str, Any], persistent: bool = True):
        properties = pika.BasicProperties(delivery_mode=2) if persistent else None
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=properties
        )
        logger.info(f"Message published to exchange {exchange_name} with routing key {routing_key}: {message}")

# Example usage:
# messaging_service = MessagingService(rabbitmq_url='amqp://guest:guest@localhost:5672/')
# messaging_service.connect()
# messaging_service.declare_queue('test_queue')
# messaging_service.publish_message('test_queue', {'key': 'value'})
# messaging_service.consume_messages('test_queue', lambda msg: print(f"Received message: {msg}"))
# messaging_service.close_connection()