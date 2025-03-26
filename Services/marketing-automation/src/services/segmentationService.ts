// src/services/segmentationService.ts
import { Pool } from 'pg';
import { logger } from '../utils/logger';

const pool = new Pool();

export const getSegments = async () => {
  try {
    const res = await pool.query('SELECT * FROM segments');
    return res.rows;
  } catch (error) {
    logger.error('Error fetching segments:', error);
    throw error;
  }
};
