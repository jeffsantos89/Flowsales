import { Request, Response, NextFunction } from 'express';
import { ValidationError } from 'express-validation';
import { JsonWebTokenError } from 'jsonwebtoken';
// import { CustomError } from '../errors/customError'; // Supondo que você tenha uma classe de erro personalizada

export const errorHandler = (err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error(`[${new Date().toISOString()}] ${err.stack}`);

  if (err instanceof ValidationError) {
    return res.status(400).json({
      error: 'Erro de validação',
      details: err.details,
    });
  }

  if (err instanceof JsonWebTokenError) {
    return res.status(401).json({
      error: 'Token inválido',
      message: err.message,
    });
  }

  if (err instanceof CustomError) {
    return res.status(err.statusCode).json({
      error: err.name,
      message: err.message,
    });
  }

  return res.status(500).json({
    error: 'Ocorreu um erro no servidor',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Erro interno do servidor',
  });
};

// Exemplo de uso em outro arquivo
import { CustomError } from '../errors/CustomError';

// Lançar um erro 404 - Not Found
throw new CustomError('Recurso não encontrado', 404);

// Lançar um erro 403 - Forbidden
throw new CustomError('Acesso negado', 403);

// Lançar um erro 400 - Bad Request
throw new CustomError('Dados inválidos', 400);

// Lançar um erro 500 - Server Error (padrão se não especificado)
throw new CustomError('Erro interno do servidor');