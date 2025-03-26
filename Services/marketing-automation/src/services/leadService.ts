import { getCache, setCache } from '../cache/redisCache';
import { Pool } from 'pg';

const pool = new Pool();

export const getLeads = async () => {
  const cacheKey = 'leads';
  const cachedLeads = await getCache(cacheKey);
  if (cachedLeads) return cachedLeads;

  const res = await pool.query('SELECT * FROM leads');
  await setCache(cacheKey, res.rows);
  return res.rows;
};
