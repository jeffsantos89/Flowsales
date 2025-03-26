import { executeShardQuery } from '../database/shardManager';
import { Pool } from 'pg';

jest.mock('pg', () => {
  const mPool = {
    query: jest.fn(),
  };
  return { Pool: jest.fn(() => mPool) };
});

describe('Sharding Service', () => {
  const pool = new Pool();

  it('should execute query on the correct shard', async () => {
    pool.query.mockResolvedValueOnce({ rows: [{ id: 1, name: 'Test' }] });
    const result = await executeShardQuery('123', 'SELECT * FROM leads');
    expect(result).toEqual({ rows: [{ id: 1, name: 'Test' }] });
  });
});
