// src/security/securityPolicies.ts
import { Request, Response, NextFunction } from 'express';

export const securityHeaders = (req: Request, res: Response, next: NextFunction) => {
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  next();
};
