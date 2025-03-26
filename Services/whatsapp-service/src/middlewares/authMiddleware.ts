import { Request, Response, NextFunction } from 'express';

export const authMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const token = req.headers.authorization;

  if (!token) {
    res.status(401).json({ message: 'Unauthorized' });
    return;
  }

  try {
    // Lógica de verificação do token aqui
    // Se o token for válido, chame next()
    next();
  } catch (error) {
    res.status(401).json({ message: 'Unauthorized' });
  }
};
