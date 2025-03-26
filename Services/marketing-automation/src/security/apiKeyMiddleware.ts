// src/security/apiKeyMiddleware.ts
import { Request, Response, NextFunction } from 'express';
import { logger } from '../logs/logService';

const VALID_API_KEYS = [
  process.env.ADMIN_API_KEY || 'admin-secret-api-key',
];

export const apiKeyMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const apiKey = req.header('X-API-Key');
  if (!apiKey || !VALID_API_KEYS.includes(apiKey)) {
    logger.warn('Unauthorized access attempt');
    return res.status(401).json({ message: 'Unauthorized' });
  }
  next();
};
