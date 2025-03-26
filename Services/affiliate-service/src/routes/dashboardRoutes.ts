import { NextFunction, Request, Response, Router } from 'express';
import { celebrate, Joi, Segments } from 'celebrate';
import { authMiddleware } from '../middlewares/authMiddleware';
import rateLimit from 'express-rate-limit';
import logger from '../utils/logger'; // Logger estruturado
import { createClient } from 'redis';

const router = Router();

// Conexão opcional com Redis para cache (se disponível)
const redisClient = createClient({
  socket: {
    host: process.env.REDIS_HOST || 'localhost',
    port: Number(process.env.REDIS_PORT) || 6379,
  },
});

redisClient
  .connect()
  .catch((err) => logger.error(`Redis Connection Error: ${err.message}`));

// Middleware avançado para capturar erros de forma automática
const asyncHandler = <T = unknown>(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<T>
) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    Promise.resolve(fn(req, res, next)).catch((err) => {
      logger.error(`[ERROR] ${req.method} ${req.url} - ${err.message}`);
      next(err);
    });
  };
};

// Middleware para medir o tempo de resposta da API
router.use((req: Request, res: Response, next: NextFunction) => {
  const start = process.hrtime();
  res.on('finish', () => {
    const [seconds, nanoseconds] = process.hrtime(start);
    const durationMs = (seconds * 1000 + nanoseconds / 1e6).toFixed(2);
    logger.info(
      `[${req.method}] ${req.url} - ${res.statusCode} - ${durationMs}ms`
    );
  });
  next();
});

// Configuração dinâmica de Rate Limit baseado no tipo de usuário
router.use((req: Request, res: Response, next: NextFunction) => {
  const limit = req.user ? 200 : 100;
  rateLimit({
    windowMs: 15 * 60 * 1000,
    max: limit,
    message:
      'Too many requests from this IP, please try again after 15 minutes',
    standardHeaders: true,
    legacyHeaders: false,
  })(req, res, next);
});

// Validação avançada dos query params
const dashboardValidation = {
  [Segments.QUERY]: Joi.object().keys({
    startDate: Joi.date().iso().optional(),
    endDate: Joi.date().iso().optional(),
    filter: Joi.string().valid('sales', 'users', 'traffic').optional(),
  }),
};

// Lógica do dashboard altamente otimizada com cache e logs estruturados
async function dashboard(req: Request, res: Response): Promise<void> {
  const { startDate, endDate, filter } = req.query;
  const cacheKey = `dashboard:${startDate}-${endDate}-${filter}`;

  try {
    // Verifica se os dados já estão no cache do Redis
    const cachedData = await redisClient.get(cacheKey);
    if (cachedData) {
      logger.info(`Cache hit for ${cacheKey}`);
      res.json(JSON.parse(cachedData));
      return;
    }

    logger.info(`Cache miss for ${cacheKey}, processing request...`);

    // Simulação de consulta ao banco de dados
    const data = await fetchDashboardData(
      startDate as string,
      endDate as string,
      filter as string
    );

    // Armazena no cache do Redis por 10 minutos
    await redisClient.setEx(cacheKey, 600, JSON.stringify(data));

    res.json(data);
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error occurred';
    logger.error(`[ERROR] Dashboard processing failed: ${errorMessage}`);
    res.status(500).json({ message: 'Internal Server Error' });
  }
}

// Simulação de função para busca de dados do dashboard
async function fetchDashboardData(
  startDate?: string,
  endDate?: string,
  filter?: string
) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ startDate, endDate, filter, result: 'Sample Data' });
    }, 500); // Simula um tempo de resposta de 500ms
  });
}

// Rota protegida com autenticação, validação e tratamento avançado de erros
router.get(
  '/',
  authMiddleware, // Proteção por autenticação
  celebrate(dashboardValidation), // Validação refinada dos parâmetros
  asyncHandler(dashboard) // Execução segura do handler
);

interface CustomError extends Error {
  status?: number;
  stack?: string;
}

// Middleware global para tratamento avançado de erros
router.use((err: unknown, req: Request, res: Response) => {
  const error = err as CustomError;
  logger.error(`[ERROR] ${req.method} ${req.url} - ${error.message}`);
  const statusCode = error.status || 500;
  res.status(statusCode).json({
    message: error.message || 'Internal Server Error',
    error: process.env.NODE_ENV === 'development' ? error.stack : undefined,
  });
});

export default router;
