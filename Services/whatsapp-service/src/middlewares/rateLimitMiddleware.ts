import rateLimit from 'express-rate-limit';
import { Request, Response, NextFunction } from 'express';
import { HttpException } from '../exceptions/HttpException';

export const rateLimitMiddleware = rateLimit({
  windowMs: 10 * 60 * 1000, // 10 minutos
  max: 50, // Limite de 50 requisições por IP
  message: 'Você excedeu o limite de requisições, tente novamente mais tarde.',
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req: Request, res: Response, next: NextFunction, options) => {
    return res.status(429).json({
      error: 'Rate limit exceeded',
      message: options.message
    });
  }
});
