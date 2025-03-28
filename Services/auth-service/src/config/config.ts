import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

interface DatabaseConfig {
    host: string;
    port: number;
    username: string;
    password: string;
    database: string;
}

interface JWTConfig {
    secret: string;
    expiresIn: string;
    refreshTokenExpiresIn: string;
}

interface RedisConfig {
    host: string;
    port: number;
    password: string | null;
}

interface AppConfig {
    environment: 'development' | 'production' | 'test';
    port: number;
    apiVersion: string;
    corsOrigins: string[];
}

interface Config {
    app: AppConfig;
    database: DatabaseConfig;
    jwt: JWTConfig;
    redis: RedisConfig;
}

const validateEnvVariables = (): void => {
    const requiredEnvVars = [
        'NODE_ENV',
        'PORT',
        'DB_HOST',
        'DB_PORT',
        'DB_USER',
        'DB_PASS',
        'DB_NAME',
        'JWT_SECRET',
        'REDIS_HOST',
        'REDIS_PORT',
    ];

    for (const envVar of requiredEnvVars) {
        if (!process.env[envVar]) {
            throw new Error(`Missing required environment variable: ${envVar}`);
        }
    }
};

validateEnvVariables();

const config: Config = {
    app: {
        environment: (process.env.NODE_ENV as 'development' | 'production' | 'test') || 'development',
        port: parseInt(process.env.PORT || '3000', 10),
        apiVersion: 'v1',
        corsOrigins: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['http://localhost:3000'],
    },
    database: {
        host: process.env.DB_HOST!,
        port: parseInt(process.env.DB_PORT!, 10),
        username: process.env.DB_USER!,
        password: process.env.DB_PASS!,
        database: process.env.DB_NAME!,
    },
    jwt: {
        secret: process.env.JWT_SECRET!,
        expiresIn: process.env.JWT_EXPIRES_IN || '1h',
        refreshTokenExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
    },
    redis: {
        host: process.env.REDIS_HOST!,
        port: parseInt(process.env.REDIS_PORT!, 10),
        password: process.env.REDIS_PASSWORD || null,
    },
};

// Freeze the configuration object to prevent modifications during runtime
Object.freeze(config);
Object.freeze(config.app);
Object.freeze(config.database);
Object.freeze(config.jwt);
Object.freeze(config.redis);

export default config;