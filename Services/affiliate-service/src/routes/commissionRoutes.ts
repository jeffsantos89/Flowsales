import { Router } from 'express';
import { celebrate, Joi, Segments } from 'celebrate';
import {
  addCommission,
  listCommissions,
} from '../controllers/commissionController';
import { authMiddleware } from '../middlewares/authMiddleware';
import { rateLimitMiddleware } from '../middlewares/rateLimitMiddleware';
import asyncHandler from '../utils/asyncHandler';

const router = Router();

// Validação das entradas com celebrate (baseado em Joi)
const commissionValidation = {
  [Segments.BODY]: Joi.object().keys({
    amount: Joi.number().positive().required(),
    status: Joi.string().valid('pending', 'approved', 'rejected').required(),
    affiliateId: Joi.number().required(),
  }),
};

// Middleware de Rate Limiting para evitar abusos (opcional)
router.use(rateLimitMiddleware);

// Rotas
router.post(
  '/add',
  authMiddleware, // Middleware de autenticação
  celebrate(commissionValidation), // Validação de entrada
  asyncHandler(addCommission) // Handler com tratamento automático de erros
);

router.get(
  '/',
  authMiddleware, // Middleware de autenticação
  asyncHandler(listCommissions) // Handler com tratamento automático de erros
);

export default router;
