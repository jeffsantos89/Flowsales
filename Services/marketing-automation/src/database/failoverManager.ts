// src/database/failoverManager.ts
import { Pool } from 'pg';
import { logger } from '../utils/logger';

const primaryDb = new Pool({
  host: process.env.PRIMARY_DB_HOST || 'postgres-primary',
  user: 'postgres',
  password: 'postgres',
  database: 'flowsale',
});

const secondaryDb = new Pool({
  host: process.env.SECONDARY_DB_HOST || 'postgres-secondary',
  user: 'postgres',
  password: 'postgres',
  database: 'flowsale',
});

let isPrimaryActive = true;

export const executeFailoverQuery = async (query: string) => {
  try {
    const res = isPrimaryActive
      ? await primaryDb.query(query)
      : await secondaryDb.query(query);
    return res.rows;
  } catch (error) {
    logger.error('Primary DB failed, switching to secondary.');
    isPrimaryActive = false;
    return await secondaryDb.query(query);
  }
};
