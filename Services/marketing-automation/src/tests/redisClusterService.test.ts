import { getCache, setCache } from '../cache/redisClusterService';

jest.mock('ioredis', () => ({
  Cluster: jest.fn().mockImplementation(() => ({
    get: jest.fn().mockResolvedValue('{"data":"test"}'),
    set: jest.fn().mockResolvedValue('OK'),
  })),
}));

describe('Redis Cluster Service', () => {
  it('should get cache', async () => {
    const result = await getCache('test-key');
    expect(result).toEqual({ data: 'test' });
  });

  it('should set cache', async () => {
    await setCache('test-key', { data: 'test' });
  });
});
