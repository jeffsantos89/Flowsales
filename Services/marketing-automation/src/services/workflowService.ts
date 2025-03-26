// src/services/workflowService.ts
import { Pool } from 'pg';
import { logger } from '../utils/logger';

const pool = new Pool();

export const createWorkflow = async (workflowData: any) => {
  try {
    const query = 'INSERT INTO workflows (name, steps) VALUES ($1, $2) RETURNING *';
    const values = [workflowData.name, JSON.stringify(workflowData.steps)];
    const res = await pool.query(query, values);
    return res.rows[0];
  } catch (error) {
    logger.error('Error creating workflow:', error);
    throw error;
  }
};
