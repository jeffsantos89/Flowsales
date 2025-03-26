// src/performance/cacheService.ts
import { redisClient } from '../config/redisConfig';
import { promisify } from 'util';

const getAsync = promisify(redisClient.get).bind(redisClient);
const setAsync = promisify(redisClient.set).bind(redisClient);

export const getFromCache = async (key: string) => {
  const data = await getAsync(key);
  return data ? JSON.parse(data) : null;
};

export const saveToCache = async (key: string, value: object, ttl = 3600) => {
  await setAsync(key, JSON.stringify(value), 'EX', ttl);
};
