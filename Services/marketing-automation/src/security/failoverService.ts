// src/security/failoverService.ts
import { Pool } from 'pg';

const primaryDb = new Pool({
  host: process.env.PRIMARY_DB_HOST,
  user: 'postgres',
  password: 'postgres',
  database: 'flowsale',
});

const secondaryDb = new Pool({
  host: process.env.SECONDARY_DB_HOST,
  user: 'postgres',
  password: 'postgres',
  database: 'flowsale',
});

export const executeQuery = async (query: string) => {
  try {
    const res = await primaryDb.query(query);
    return res.rows;
  } catch (error) {
    console.warn('Primary DB failed, switching to secondary.');
    const res = await secondaryDb.query(query);
    return res.rows;
  }
};
