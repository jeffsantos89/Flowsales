import { Request, Response, NextFunction } from 'express';

export const errorMiddleware = (err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(`[ERROR] ${err.message}`);
  res.status(500).json({
    message: 'Internal Server Error',
    error: err.message,
  });
};
