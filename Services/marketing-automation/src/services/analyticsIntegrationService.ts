// src/services/analyticsService.ts
import { Pool } from 'pg';
import { logger } from '../utils/logger';

const pool = new Pool();

export const getAnalyticsData = async () => {
  try {
    const res = await pool.query('SELECT * FROM analytics');
    return res.rows;
  } catch (error) {
    logger.error('Error fetching analytics data:', error);
    throw error;
  }
};
