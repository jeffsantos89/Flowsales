import { Kafka, logLevel } from 'kafkajs';
import logger from '../utils/logger';

const {
  KAFKA_BROKER,
  KAFKA_CLIENT_ID,
  KAFKA_USERNAME,
  KAFKA_PASSWORD,
  KAFKA_SSL,
} = process.env;

if (!KAFKA_BROKER || !KAFKA_CLIENT_ID) {
  logger.error('Variáveis KAFKA_BROKER ou KAFKA_CLIENT_ID não definidas.');
  process.exit(1);
}

const kafka = new Kafka({
  clientId: KAFKA_CLIENT_ID,
  brokers: KAFKA_BROKER.split(','),
  ssl: KAFKA_SSL === 'true',
  sasl:
    KAFKA_USERNAME && KAFKA_PASSWORD
      ? {
          mechanism: 'plain',
          username: KAFKA_USERNAME,
          password: KAFKA_PASSWORD,
        }
      : undefined,
  logLevel: logLevel.INFO,
  logCreator:
    () =>
    ({ namespace, level, label, log }) => {
      const { message, ...extra } = log;
      logger.info(`[${label}] ${message}`, { namespace, level, ...extra });
    },
});

export default kafka;
