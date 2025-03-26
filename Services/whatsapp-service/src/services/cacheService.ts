import Redis, { RedisOptions } from 'ioredis';
import { config } from '../config';

interface ICacheOptions {
  ttl?: number;
  prefix?: string;
}

class CacheService {
  private readonly redis: Redis;
  private readonly defaultTTL: number = 3600;
  private readonly prefix: string = 'cache:';

  constructor(options?: RedisOptions) {
    this.redis = new Redis({
      host: process.env.REDIS_HOST || config.redisHost || 'localhost',
      port: config.redisPort || 6379,
      retryStrategy: (times: number) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      maxRetriesPerRequest: 3,
      ...options
    });

    this.redis.on('error', (error) => {
      console.error('Redis connection error:', error);
    });
  }

  private getKey(key: string, prefix?: string): string {
    return `${prefix || this.prefix}${key}`;
  }

  async get<T>(key: string, options?: ICacheOptions): Promise<T | null> {
    try {
      const data = await this.redis.get(this.getKey(key, options?.prefix));
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }

  async set<T>(key: string, value: T, options?: ICacheOptions): Promise<boolean> {
    try {
      const ttl = options?.ttl || this.defaultTTL;
      await this.redis.set(
        this.getKey(key, options?.prefix),
        JSON.stringify(value),
        'EX',
        ttl
      );
      return true;
    } catch (error) {
      console.error('Cache set error:', error);
      return false;
    }
  }

  async delete(key: string, prefix?: string): Promise<boolean> {
    try {
      await this.redis.del(this.getKey(key, prefix));
      return true;
    } catch (error) {
      console.error('Cache delete error:', error);
      return false;
    }
  }

  async clear(pattern: string = '*'): Promise<boolean> {
    try {
      const keys = await this.redis.keys(`${this.prefix}${pattern}`);
      if (keys.length) {
        await this.redis.del(...keys);
      }
      return true;
    } catch (error) {
      console.error('Cache clear error:', error);
      return false;
    }
  }
}

export const cacheService = new CacheService();