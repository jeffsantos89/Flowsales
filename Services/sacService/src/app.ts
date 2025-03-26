import * as express from 'express';
import helmet from 'helmet';
import * as compression from 'compression';
import { traceMiddleware } from './middlewares/traceMiddleware';  // Caminho corrigido
import { rateLimiter } from './middlewares/rateLimitMiddleware';
import { setupSwagger } from './config/swaggerConfig';
import { errorHandler } from './middlewares/errorHandler';
import { config } from 'dotenv';
config();

const app = express();

// Configurações de segurança
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'"],
        objectSrc: ["'none'"],
        upgradeInsecureRequests: [],
      },
    },
    referrerPolicy: { policy: 'strict-origin' },
    crossOriginResourcePolicy: { policy: 'same-origin' },
  })
);

// Middleware de rastreamento
app.use(traceMiddleware);

// Middleware de limitação de taxa
app.use(rateLimiter);

// Configuração do Swagger
setupSwagger(app);

// Middleware de compressão
app.use(compression());

// Middleware de tratamento de erros
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  errorHandler(err, req, res, next);
});

// Iniciar o servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

export default app;
