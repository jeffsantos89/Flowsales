// src/security/mtlsMiddleware.ts
import { Request, Response, NextFunction } from 'express';

export const mtlsMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const clientCert = req.socket.getPeerCertificate();
  if (!req.client.authorized) {
    return res.status(401).send('Unauthorized');
  }
  console.log('Client certificate:', clientCert);
  next();
};

