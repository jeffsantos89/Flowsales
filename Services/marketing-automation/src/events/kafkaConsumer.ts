import { consumer } from '../config/kafkaConfig';
import { logger } from '../utils/logger';

export const consumeEvents = async () => {
  await consumer.connect();
  await consumer.subscribe({ topic: 'email-events', fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ message }) => {
      logger.info(`Mensagem recebida: ${message.value?.toString()}`);
      // Processar a mensagem...
    },
  });
};
