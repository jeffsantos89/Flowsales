import { Request, Response, NextFunction } from 'express';

interface CustomRequest extends Request {
    user?: {
        role: string;
    };
}
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import Redis from 'ioredis';
import * as winston from 'winston';

// Configuração do logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: 'rate-limit.log' })
    ],
});

// Configuração do Redis
const redisClient = new Redis({
    port: 6379,
    password: 'your_redis_password',
});

// Função para determinar o limite de requisições dinamicamente
const dynamicRateLimit = (req: CustomRequest): number => {
    // Exemplo: Limite diferente para usuários autenticados
    if (req.user && req.user.role === 'premium') {
        return 200;
    }
    return 100;
};

export const rateLimiter = rateLimit({
    store: new RedisStore({
        // Use uma função que corresponda à assinatura esperada pelo RedisStore
        sendCommand: async (command: string, ...args: string[]) => {
            return redisClient.call(command, ...args);
        },
    }),
    windowMs: 15 * 60 * 1000, // 15 minutos
    max: (req: Request) => dynamicRateLimit(req as CustomRequest),
    standardHeaders: true,
    legacyHeaders: false,
    message: (req: Request, res: Response) => {
        return {
            message: 'Muitas requisições, por favor tente novamente mais tarde',
            retryAfter: res.getHeaders()['Retry-After'],
        };
    },
    onLimitReached: (req: Request, res: Response, optionsUsed: any) => {
        logger.warn(`Rate limit exceeded for IP: ${req.ip}`);
    },
});