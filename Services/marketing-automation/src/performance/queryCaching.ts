// src/performance/queryCaching.ts
import { getCache, setCache } from '../cache/redisClusterService';
import { Pool } from 'pg';
import { logger } from '../logs/logService';

const pool = new Pool();

export const cachedQuery = async (query: string, key: string) => {
  const cached = await getCache(key);
  if (cached) {
    logger.info(`Cache hit for ${key}`);
    return cached;
  }

  logger.info(`Cache miss for ${key}`);
  const { rows } = await pool.query(query);
  await setCache(key, rows);
  return rows;
};
