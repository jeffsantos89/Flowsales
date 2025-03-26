import { setCache, getCache } from '../cache/redisCache';
import { redisClient } from '../config/redisConfig';

jest.mock('redis', () => ({
  createClient: jest.fn(() => ({
    get: jest.fn(),
    set: jest.fn(),
  })),
}));

describe('Redis Cache', () => {
  it('should set and get cache data', async () => {
    await setCache('test-key', { data: 'test' });
    const data = await getCache('test-key');
    expect(data).toEqual({ data: 'test' });
  });
});
