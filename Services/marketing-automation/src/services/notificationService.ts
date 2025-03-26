// src/services/notificationService.ts
import { Kafka } from 'kafkajs';
import { logger } from '../utils/logger';

const kafka = new Kafka({ brokers: ['kafka:9092'] });
const producer = kafka.producer();

export const sendNotification = async (message: string) => {
  try {
    await producer.connect();
    await producer.send({
      topic: 'notifications',
      messages: [{ value: message }],
    });
    await producer.disconnect();
  } catch (error) {
    logger.error('Error sending notification:', error);
    throw error;
  }
};
