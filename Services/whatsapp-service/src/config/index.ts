import dotenv from 'dotenv';

dotenv.config();

export const config = {
  apiUrl: process.env.WHATSAPP_API_URL || '',
  apiToken: process.env.WHATSAPP_API_TOKEN || '',
  phoneNumberId: process.env.WHATSAPP_PHONE_NUMBER_ID || '',
  jwtSecret: process.env.JWT_SECRET || (() => { throw new Error('JWT_SECRET env var is required'); })(),
  redisHost: process.env.REDIS_HOST || 'redis',
  redisPort: parseInt(process.env.REDIS_PORT || '6379', 10),
  postgresHost: process.env.POSTGRES_HOST || 'postgres',
  postgresUser: process.env.POSTGRES_USER || 'postgres',
  postgresPassword: process.env.POSTGRES_PASSWORD || 'postgres',
  postgresDb: process.env.POSTGRES_DB || 'whatsapp_service',
};
