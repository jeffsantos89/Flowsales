// src/cache/redisCache.ts
import redis from 'redis';
import { promisify } from 'util';

const redisClient = redis.createClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379', 10),
});

const getAsync = promisify(redisClient.get).bind(redisClient);
const setAsync = promisify(redisClient.set).bind(redisClient);

export const getCache = async (key: string) => {
  const data = await getAsync(key);
  return data ? JSON.parse(data) : null;
};

export const setCache = async (key: string, value: object, expireTime = 3600) => {
  await setAsync(key, JSON.stringify(value), 'EX', expireTime);
};
