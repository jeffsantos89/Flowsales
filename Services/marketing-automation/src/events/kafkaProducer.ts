import { producer } from '../config/kafkaConfig';
import { logger } from '../utils/logger';

export const sendEvent = async (topic: string, message: object) => {
  await producer.connect();
  await producer.send({
    topic,
    messages: [{ value: JSON.stringify(message) }],
  });
  await producer.disconnect();
  logger.info(`Evento enviado para o tópico ${topic}`);
};
