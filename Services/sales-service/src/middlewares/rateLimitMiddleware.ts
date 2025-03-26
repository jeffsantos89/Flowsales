import rateLimit from 'express-rate-limit';

export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limite de 100 requisições por IP
  message: 'Too many requests, please try again later.',
});
