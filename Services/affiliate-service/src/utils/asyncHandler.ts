import { NextFunction, Request, Response } from 'express';
import logger from './logger'; // Importe seu logger

/**
 * Middleware para capturar erros assíncronos em rotas do Express.
 * Garante que os erros sejam passados corretamente ao `next()`.
 *
 * @param fn Função assíncrona a ser tratada
 * @returns Função middleware Express com tratamento de erros
 */
const asyncHandler = <T = unknown>(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<T>
) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    Promise.resolve(fn(req, res, next)).catch((err: Error) => {
      logger.error({
        message: `[ERROR] ${req.method} ${req.path} - ${err.message}`,
        stack: err.stack,
        user: req.user, // Se você tiver informações do usuário na requisição
      });
      next(err);
    });
  };
};

export default asyncHandler;
