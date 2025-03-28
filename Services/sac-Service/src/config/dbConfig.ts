import { DataSource } from 'typeorm';
import { ConfigError } from '../errors/configError';

export class DatabaseConfig {
  private static instance: DataSource;

  private constructor() {} // Prevent direct construction

  static async initialize(): Promise<DataSource> {
    if (this.instance) {
      return this.instance;
    }

    try {
      this.instance = new DataSource({
        type: 'postgres',
        host: process.env.DB_HOST || 'localhost',
        port: parseInt(process.env.DB_PORT || '5432'),
        username: process.env.DB_USER || 'postgres',
        password: process.env.DB_PASSWORD || 'postgres',
        database: process.env.DB_NAME || 'sac',
        entities: ['src/entities/**/*.ts'],
        migrations: ['src/migrations/**/*.ts'],
        synchronize: process.env.NODE_ENV === 'development', // Be careful with this in production
        logging: process.env.NODE_ENV === 'development',
        ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false,
      });

      await this.instance.initialize();
      console.log('PostgreSQL connection established successfully');
      return this.instance;
    } catch (error) {
      console.error('Failed to connect to PostgreSQL:', error);
      throw new ConfigError('Database connection failed');
    }
  }

  static async getConnection(): Promise<DataSource> {
    if (!this.instance) {
      return this.initialize();
    }
    return this.instance;
  }

  static async closeConnection(): Promise<void> {
    if (this.instance) {
      await this.instance.destroy();
      this.instance = null;
    }
  }
}
