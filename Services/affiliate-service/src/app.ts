import express, { Application, NextFunction, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import morgan from 'morgan';
import rfs from 'rotating-file-stream';
import path from 'path';
import { createNamespace } from 'cls-hooked';
import swaggerUi from 'swagger-ui-express';
import swaggerDocument from './swagger.json';

// Rotas
import { RouterRegistry } from './routes';

// Middlewares
import errorHandler from './middlewares/errorMiddleware';
import { securityMiddleware } from './security/httpSecurity';
import { requestIdMiddleware } from './middlewares/requestIdMiddleware';
import { corsOptions } from './config/corsConfig';
import { CorrelationIdMiddleware } from './middlewares/correlationIdMiddleware';
import { MetricsMiddleware } from './middlewares/metricsMiddleware';

class App {
  private readonly app: Application;
  private readonly namespace = createNamespace('app-namespace');
  private readonly metricsMiddleware: MetricsMiddleware;

  constructor() {
    this.app = express();
    this.metricsMiddleware = new MetricsMiddleware();
    this.initializeApp();
  }

  private initializeApp(): void {
    this.setupSecurity();
    this.setupMiddlewares();
    this.setupDocumentation();
    this.setupMetrics();
    this.setupRoutes();
    this.setupErrorHandling();
  }

  private setupSecurity(): void {
    this.app.use(
      helmet({
        contentSecurityPolicy: process.env.NODE_ENV === 'production',
        crossOriginEmbedderPolicy: process.env.NODE_ENV === 'production',
      })
    );
    this.app.use(cors(corsOptions));
    this.app.use(securityMiddleware);

    // Rate limiting with different rules for different endpoints
    const apiLimiter = rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 100,
      message: 'Too many requests from this IP, please try again later.',
      standardHeaders: true,
      legacyHeaders: false,
    });

    const authLimiter = rateLimit({
      windowMs: 60 * 60 * 1000,
      max: 5,
      message: 'Too many auth attempts from this IP, please try again later.',
    });

    this.app.use('/api/', apiLimiter);
    this.app.use('/api/v1/auth', authLimiter);
  }

  private setupMiddlewares(): void {
    // Logging setup with rotation and compression
    const accessLogStream = rfs('access.log', {
      interval: '1d',
      path: path.join(__dirname, 'logs'),
      compress: true,
      size: '10M',
    });

    this.app.use(
      morgan('combined', {
        stream: accessLogStream,
        skip: (req) => req.url === '/health' || req.url === '/metrics',
      })
    );

    this.app.use(compression({ level: 6 }));
    this.app.use(
      express.json({
        limit: '10mb',
        strict: true,
        verify: (req, res, buf) => {
          req['rawBody'] = buf;
        },
      })
    );
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    this.app.use(this.namespace.middleware.bind(this.namespace));
    this.app.use(requestIdMiddleware);
    this.app.use(new CorrelationIdMiddleware().handle);
  }

  private setupDocumentation(): void {
    this.app.use(
      '/api-docs',
      swaggerUi.serve,
      swaggerUi.setup(swaggerDocument)
    );
  }

  private setupMetrics(): void {
    this.app.use(this.metricsMiddleware.handle);
    this.app.get('/metrics', this.metricsMiddleware.getMetrics);
  }

  private setupRoutes(): void {
    new RouterRegistry(this.app).registerRoutes();
  }

  private setupErrorHandling(): void {
    // 404 handler
    this.app.use((req: Request, res: Response, next: NextFunction) => {
      res.status(404).json({
        error: 'Not Found',
        path: req.originalUrl,
      });
    });

    // Global error handler
    this.app.use(
      (err: any, req: Request, res: Response, next: NextFunction) => {
        errorHandler(err, req, res, next);
      }
    );

    // Unhandled rejection handler
    process.on('unhandledRejection', (reason, promise) => {
      console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    });

    // Uncaught exception handler
    process.on('uncaughtException', (error) => {
      console.error('Uncaught Exception:', error);
      process.exit(1);
    });
  }

  public getApp(): Application {
    return this.app;
  }
}

export default new App().getApp();
