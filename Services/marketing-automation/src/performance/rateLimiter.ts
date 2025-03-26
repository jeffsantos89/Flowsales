// src/performance/rateLimiter.ts
import rateLimit from 'express-rate-limit';

export const advancedRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 200,
  message: 'Too many requests, please try again later.',
  keyGenerator: (req) => req.ip,
  handler: (req, res) => {
    res.status(429).json({ message: 'Rate limit exceeded' });
  },
});
import rateLimit from 'express-rate-limit';

export const apiKeyRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 500,
  keyGenerator: (req) => req.header('X-API-Key') || req.ip,
  message: 'Too many requests, please try again later.',
});
