// src/performance/queryOptimizer.ts
import { Pool } from 'pg';

const pool = new Pool();

export const optimizeQuery = async (query: string) => {
  const explainQuery = `EXPLAIN ANALYZE ${query}`;
  const { rows } = await pool.query(explainQuery);
  console.log('Query Optimization Report:', rows);
  return rows;
};
// src/performance/queryOptimizer.ts
import { Pool } from 'pg';
import { logger } from '../utils/logger';

const pool = new Pool();

export const addIndex = async (table: string, column: string) => {
  try {
    const query = `CREATE INDEX IF NOT EXISTS idx_${table}_${column} ON ${table} (${column})`;
    await pool.query(query);
    logger.info(`Index created on ${table}(${column})`);
  } catch (error) {
    logger.error('Error creating index:', error);
  }
};
