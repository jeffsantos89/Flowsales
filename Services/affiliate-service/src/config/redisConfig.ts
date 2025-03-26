import { createClient, RedisClientType } from 'redis';
import logger from '../utils/logger';

const redisUrl =
  process.env.REDIS_URL ||
  `redis://${process.env.REDIS_HOST || 'localhost'}:6379`;

const redisClient: RedisClientType = createClient({
  url: redisUrl,
  socket: {
    reconnectStrategy: (retries: number) => Math.min(retries * 100, 3000),
    tls: process.env.REDIS_USE_TLS === 'true' ? true : undefined,
  },
  password: process.env.REDIS_PASSWORD,
});

// Gerenciamento avançado de eventos para robustez e observabilidade
redisClient.on('connect', () => logger.info('[Redis] Connected successfully.'));
redisClient.on('error', (error) =>
  logger.error(`[Redis] Error connecting: ${error.message}`, { error })
);
redisClient.on('reconnecting', () =>
  logger.warn('[Redis] Attempting reconnection...')
);
redisClient.on('ready', () => logger.info('[Redis] Connection ready.'));
redisClient.on('end', () => logger.warn('[Redis] Connection closed.'));

redisClient.connect().catch((error) => {
  logger.error(`[Redis] Connection failed: ${error.message}`, { error });
  process.exit(1); // Garante que a aplicação não siga rodando sem Redis disponível.
});

export default redisClient;
