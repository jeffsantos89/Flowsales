import { getAnalyticsData } from '../services/analyticsService';
import { Pool } from 'pg';

jest.mock('pg', () => {
  const mPool = {
    query: jest.fn(),
    connect: jest.fn(),
    end: jest.fn(),
  };
  return { Pool: jest.fn(() => mPool) };
});

describe('Analytics Service', () => {
  const pool = new Pool();

  it('should fetch analytics data', async () => {
    const mockData = [{ id: 1, metric: 'views', count: 100 }];
    pool.query.mockResolvedValueOnce({ rows: mockData });

    const data = await getAnalyticsData();
    expect(data).toEqual(mockData);
    expect(pool.query).toHaveBeenCalledWith('SELECT * FROM analytics');
  });
});
