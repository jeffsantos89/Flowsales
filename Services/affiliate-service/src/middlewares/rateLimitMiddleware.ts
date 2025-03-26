// filepath: src/middlewares/rateLimitMiddleware.ts
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { createClient } from 'redis';
import { Request, Response } from 'express';

// Configuração do Redis
const redisClient = createClient({
  socket: {
    host: process.env.REDIS_HOST || 'localhost',
    port: Number(process.env.REDIS_PORT) || 6379,
  },
});

redisClient.connect().catch((err) => {
  throw new Error(`Redis connection failed: ${err.message}`);
});

// Middleware de rate limit usando Redis
export const rateLimitMiddleware = rateLimit({
  store: new RedisStore({
    sendCommand: async (...args: string[]) => redisClient.sendCommand(args),
  }),
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: (req: Request) => {
    return req.user ? 200 : 100; // Usuários autenticados têm um limite maior
  },
  message: {
    error: 'Too many requests',
    message: 'You have exceeded the request limit. Try again later.',
  },
  keyGenerator: (req: Request) => {
    return req.ip || 'unknown';
  },
  handler: (_req: Request, res: Response) => {
    res.status(429).json({
      status: 'error',
      message: 'Too many requests, please slow down!',
    });
  },
  standardHeaders: true,
  legacyHeaders: false,
});
