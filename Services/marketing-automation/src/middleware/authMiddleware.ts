// src/middleware/authMiddleware.ts
import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ message: 'Unauthorized' });

  jwt.verify(token, process.env.JWT_SECRET as string, (err, decoded) => {
    if (err) return res.status(401).json({ message: 'Invalid token' });
    next();
  });
};
