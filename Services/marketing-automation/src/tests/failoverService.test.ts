import { executeQuery } from '../security/failoverService';
import { Pool } from 'pg';

jest.mock('pg', () => {
  const mPool = {
    query: jest.fn(),
    connect: jest.fn(),
  };
  return { Pool: jest.fn(() => mPool) };
});

describe('Failover Service', () => {
  const pool = new Pool();

  it('should switch to secondary DB on failure', async () => {
    pool.query
      .mockRejectedValueOnce(new Error('Primary DB down'))
      .mockResolvedValueOnce({ rows: [{ id: 1, name: 'Test' }] });

    const res = await executeQuery('SELECT * FROM test');
    expect(res).toEqual([{ id: 1, name: 'Test' }]);
  });
});
