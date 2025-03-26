import redis from 'redis';

export const redisClient = redis.createClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379', 10),
});

redisClient.on('error', (err) => {
  console.error('Redis error:', err);
});
