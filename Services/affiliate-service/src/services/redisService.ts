import { createClient } from 'redis';
import logger from '../utils/logger';
import { Injectable } from '@nestjs/common';

@Injectable()
export class RedisService {
  async setEx(key: string, ttl: number, value: string): Promise<void> {
    try {
      await this.redisClient.setEx(key, ttl, value);
      logger.info(`Chave ${key} salva no Redis com sucesso.`);
    } catch (error) {
      logger.error(`Erro ao salvar chave ${key} no Redis: ${error}`);
    }
  }
  private redisClient;

  constructor() {
    this.redisClient = this.createRedisClient();
    this.connectRedis();
  }

  private async connectRedis() {
    try {
      await this.redisClient.connect();
      logger.info('✅ Redis conectado com sucesso');
    } catch (error) {
      logger.error('❌ Erro ao conectar ao Redis:', error);
      process.exit(1);
    }
  }

  private createRedisClient() {
    const client = createClient({
      url: process.env.REDIS_URL,
      password: process.env.REDIS_PASSWORD,
      socket: {
        reconnectStrategy: (retries) => Math.min(retries * 100, 3000),
        connectTimeout: 10000, // Timeout de 10 segundos para tentar conectar
      },
    });

    client.on('connect', () => logger.info('🟢 Redis: Tentando conectar...'));
    client.on('ready', () => logger.info('🟢 Redis: Conexão estabelecida'));
    client.on('end', () => logger.warn('⚠️ Redis: Conexão encerrada'));
    client.on('reconnecting', () =>
      logger.info('🔄 Redis: Tentando reconectar...')
    );
    client.on('error', (err) => logger.error('❌ Redis Client Error', err));

    return client;
  }

  async get<T>(key: string): Promise<T | null> {
    try {
      const data = await this.redisClient.get(key);
      return data ? (JSON.parse(data) as T) : null;
    } catch (error) {
      logger.error(`Erro ao obter chave ${key} do Redis: ${error}`);
      return null;
    }
  }

  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    try {
      const data = JSON.stringify(value);
      if (ttl) {
        await this.redisClient.setEx(key, ttl, data);
      } else {
        await this.redisClient.set(key, data);
      }
      logger.info(`Chave ${key} salva no Redis com sucesso.`);
    } catch (error) {
      logger.error(`Erro ao salvar chave ${key} no Redis: ${error}`);
    }
  }

  async delete(key: string): Promise<void> {
    try {
      await this.redisClient.del(key);
      logger.info(`Chave ${key} removida do Redis com sucesso.`);
    } catch (error) {
      logger.error(`Erro ao remover chave ${key} do Redis: ${error}`);
    }
  }
}
