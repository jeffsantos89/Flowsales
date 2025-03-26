import { NextFunction, Request, Response } from 'express';
import { body, validationResult } from 'express-validator';

export const validateAffiliate = [
  body('name').notEmpty().withMessage('O nome é obrigatório.'),
  body('email').isEmail().withMessage('E-mail inválido.'),
  body('password')
    .isLength({ min: 12 })
    .withMessage('A senha deve ter pelo menos 12 caracteres.'),

  (req: Request, res: Response, next: NextFunction) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    next();
  },
];
