import { Request, Response } from 'express';
import logger from '../utils/logger';

// Interface padrão para erros personalizados
export interface CustomError extends Error {
  status?: number;
  details?: Record<string, unknown>;
}

export class ApiError extends Error {
  status: number;
  details?: Record<string, unknown>;

  constructor(
    message: string,
    status = 500,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.status = status;
    this.details = details;
    Error.captureStackTrace(this, this.constructor);
  }
}

export const errorMiddleware = (err: ApiError, req: Request, res: Response) => {
  const status = err.status || 500;

  // Log estruturado (Winston)
  logger.error('API Error', {
    message: err.message,
    status: err.status,
    path: req.path,
    method: req.method,
    details: err.details || {},
    stack: err.stack,
  });

  // Resposta estruturada
  res.status(status).json({
    success: false,
    error: {
      message:
        process.env.NODE_ENV === 'production' && status === 500
          ? 'Internal Server Error'
          : err.message,
      ...(process.env.NODE_ENV !== 'production' && { stack: err.stack }),
      ...(err.details && { details: err.details }),
    },
  });
};

export default errorMiddleware;
