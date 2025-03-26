import 'reflect-metadata';
import { DataSource } from 'typeorm';
import { Affiliate } from '../entities/Affiliate';
import { Commission } from '../entities/Commission';
import logger from '../utils/logger';

const isProduction = process.env.NODE_ENV === 'production';

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT) || 5432,
  username: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  entities: [Affiliate, Commission],
  synchronize: !isProduction, // Nunca usar 'true' em produção
  logging: !isProduction,
  extra: {
    max: Number(process.env.DB_MAX_CONNECTIONS) || 20, // máximo de conexões no pool
    idleTimeoutMillis: 30000, // desconectar conexões inativas após 30 segundos
    connectionTimeoutMillis: 2000, // timeout ao tentar conectar
  },
});

export const initializeDatabase = async () => {
  try {
    await AppDataSource.initialize();
    logger.info('📦 Database conectado com sucesso!');
  } catch (error: unknown) {
    logger.error(
      `Falha na conexão com o database: ${
        error instanceof Error ? error.message : 'Unknown error'
      }`
    );
    process.exit(1); // encerra a aplicação em caso de falha crítica
  }
};
