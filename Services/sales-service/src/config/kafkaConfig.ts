import { Kafka } from 'kafkajs';

const kafka = new Kafka({
  clientId: 'sales-service',
  brokers: ['kafka:9092'],
});

export default kafka;
