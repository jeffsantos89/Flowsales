import { Kafka, logLevel, CompressionTypes } from 'kafkajs';
import * as tls from 'tls';

const kafka = new Kafka({
  clientId: 'sac-service',
  brokers: [process.env.KAFKA_BROKER || 'localhost:9092'],
  logLevel: logLevel.INFO,
  retry: {
    initialRetryTime: 300,
    retries: 10,
  },
  ssl: process.env.KAFKA_SSL === 'true' ? {} as tls.ConnectionOptions : undefined,
  sasl: process.env.KAFKA_SASL_USERNAME
    ? {
        mechanism: 'plain',
        username: process.env.KAFKA_SASL_USERNAME,
        password: process.env.KAFKA_SASL_PASSWORD,
      }
    : undefined,
});

export const producer = kafka.producer({
  allowAutoTopicCreation: true,
  idempotent: true,
});

export const consumer = kafka.consumer({
  groupId: process.env.KAFKA_GROUP_ID || 'sac-group',
  allowAutoTopicCreation: true,
});

export const connectKafka = async () => {
  try {
    await producer.connect();
    await consumer.connect();
    console.log('Kafka conectado com sucesso!');
  } catch (error) {
    console.error('Erro ao conectar ao Kafka:', error);
  }
};

export const sendMessage = async (topic: string, messages: any[]) => {
  try {
    await producer.send({
      topic,
      messages: messages.map(message => ({ value: JSON.stringify(message) })),
      compression: CompressionTypes.GZIP,
    });
    console.log('Mensagem enviada com sucesso!');
  } catch (error) {
    console.error('Erro ao enviar mensagem:', error);
  }
};

export const consumeMessages = async (topic: string, eachMessage: (message: any) => Promise<void>) => {
  await consumer.subscribe({ topic, fromBeginning: true });
  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const prefix = `${topic}[${partition} | ${message.offset}] / ${message.timestamp}`;
      console.log(`- ${prefix} ${message.key}#${message.value}`);
      await eachMessage(message);
    },
  });
};

