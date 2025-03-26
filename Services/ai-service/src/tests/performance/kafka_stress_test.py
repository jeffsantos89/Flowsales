import time
import json
import logging
from kafka import KafkaProducer, KafkaConsumer
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER_URL = 'localhost:9092'
TOPIC_NAME = 'stress_test_topic'
NUM_MESSAGES = 100000
NUM_CONSUMERS = 10
NUM_PRODUCERS = 10

def produce_messages(producer_id):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for i in range(NUM_MESSAGES // NUM_PRODUCERS):
        message = {'producer_id': producer_id, 'message_id': i, 'content': 'test_message'}
        producer.send(TOPIC_NAME, value=message)
        if i % 1000 == 0:
            logger.info(f'Producer {producer_id} sent {i} messages')
    producer.flush()
    producer.close()
    logger.info(f'Producer {producer_id} finished sending messages')

def consume_messages(consumer_id):
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=f'consumer_group_{consumer_id}',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    for message in consumer:
        logger.info(f'Consumer {consumer_id} received message: {message.value}')
        if message.offset % 1000 == 0:
            logger.info(f'Consumer {consumer_id} processed {message.offset} messages')
    consumer.close()

def main():
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=NUM_PRODUCERS + NUM_CONSUMERS) as executor:
        for i in range(NUM_PRODUCERS):
            executor.submit(produce_messages, i)
        for i in range(NUM_CONSUMERS):
            executor.submit(consume_messages, i)
    
    end_time = time.time()
    logger.info(f'Total time taken: {end_time - start_time} seconds')

if __name__ == '__main__':
    main()