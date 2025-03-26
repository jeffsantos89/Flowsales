// src/cache/redisClusterService.ts
import Redis from 'ioredis';

const cluster = new Redis.Cluster([
  { host: 'redis-cluster-0', port: 6379 },
  { host: 'redis-cluster-1', port: 6379 },
  { host: 'redis-cluster-2', port: 6379 },
]);

export const getCache = async (key: string) => {
  const data = await cluster.get(key);
  return data ? JSON.parse(data) : null;
};

export const setCache = async (key: string, value: object, ttl = 3600) => {
  await cluster.set(key, JSON.stringify(value), 'EX', ttl);
};
