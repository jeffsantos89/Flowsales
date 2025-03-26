import { Kafka } from 'kafkajs';

export const kafka = new Kafka({
  clientId: 'marketing-automation',
  brokers: [process.env.KAFKA_BROKER || 'localhost:9092'],
});

export const producer = kafka.producer();
export const consumer = kafka.consumer({ groupId: 'marketing-group' });
