import Redis from 'ioredis';

const redisOptions: Redis.RedisOptions = {
  host: process.env.REDIS_HOST || 'localhost',
  port: Number(process.env.REDIS_PORT) || 6379,
  retryStrategy: (times) => {
    // Reconectar após 2 segundos, exponencialmente até um máximo de 1 minuto
    const delay = Math.min(times * 50, 2000);
    return delay;
  },
  reconnectOnError: (err) => {
    const targetError = 'READONLY';
    if (err.message.includes(targetError)) {
      // Reconectar se o erro for READONLY
      return true;
    }
    return false;
  },
  maxRetriesPerRequest: null, // Desabilitar o limite de tentativas por solicitação
};

export const redisClient = new Redis(redisOptions);

redisClient.on('connect', () => console.log('Redis conectado!'));
redisClient.on('error', (err) => console.error('Erro no Redis:', err));
redisClient.on('reconnecting', () => console.log('Tentando reconectar ao Redis...'));
redisClient.on('end', () => console.log('Conexão com o Redis encerrada.'));
