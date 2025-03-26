import { Router } from 'express';
import {
  listAffiliates,
  registerAffiliate,
} from '../controllers/affiliateController';
import { authMiddleware } from '../middlewares/authMiddleware';
import { validateAffiliate } from '../validators/affiliateValidator';
import rateLimit from 'express-rate-limit';

const router = Router();

// Rate Limiter para evitar abuso de requisições
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // Limite de 100 requisições por IP
  message:
    'Muitas requisições feitas a partir deste IP, tente novamente mais tarde.',
});

// Rota para registrar um afiliado
router.post(
  '/register',
  limiter,
  authMiddleware,
  validateAffiliate, // Validação dos dados de entrada
  registerAffiliate
);

// Rota para listar afiliados
router.get('/', authMiddleware, listAffiliates);

export default router;
