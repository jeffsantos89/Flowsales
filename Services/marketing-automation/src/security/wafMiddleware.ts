// src/security/wafMiddleware.ts
import { Request, Response, NextFunction } from 'express';

export const wafMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const userAgent = req.headers['user-agent'] || '';
  if (/BadBot/.test(userAgent)) {
    return res.status(403).send('Forbidden');
  }
  next();
};
