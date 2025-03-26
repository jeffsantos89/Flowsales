import { cachedQuery } from '../performance/queryCaching';
import { getCache, setCache } from '../cache/redisClusterService';

jest.mock('../cache/redisClusterService');

describe('Query Caching', () => {
  it('should return cached data if available', async () => {
    (getCache as jest.Mock).mockResolvedValue([{ id: 1, name: 'Cached' }]);
    const result = await cachedQuery('SELECT * FROM leads', 'leads-key');
    expect(result).toEqual([{ id: 1, name: 'Cached' }]);
  });

  it('should cache data if not cached', async () => {
    (getCache as jest.Mock).mockResolvedValue(null);
    (setCache as jest.Mock).mockResolvedValue(null);
    const result = await cachedQuery('SELECT * FROM leads', 'leads-key');
    expect(setCache).toHaveBeenCalled();
  });
});
