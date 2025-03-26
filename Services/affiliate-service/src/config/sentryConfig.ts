/* eslint-disable @typescript-eslint/no-unused-vars */
import 'dotenv/config';
import * as Sentry from '@sentry/node';
import { ProfilingIntegration } from '@sentry/profiling-node';
import { Handlers } from '@sentry/node';
import { Application, NextFunction, Request, Response } from 'express';
import Logger from '../utils/logger';

const nodeProfilingIntegration = () => new ProfilingIntegration();

interface SentryConfig {
  dsn: string;
  environment: string;
  debug?: boolean;
  tracesSampleRate: number;
  profilesSampleRate: number;
  maxBreadcrumbs: number;
  attachStacktrace: boolean;
  maxValueLength: number;
}

const CONFIG: Record<string, Partial<SentryConfig>> = {
  development: {
    debug: true,
    tracesSampleRate: 1.0,
    profilesSampleRate: 1.0,
  },
  staging: {
    debug: true,
    tracesSampleRate: 0.5,
    profilesSampleRate: 0.5,
  },
  production: {
    debug: false,
    tracesSampleRate: 0.1,
    profilesSampleRate: 0.1,
  },
};

class SentryService {
  private static instance: SentryService;
  private initialized = false;
  private readonly dsn: string;
  private readonly environment: string;
  private readonly logger: typeof Logger;

  private constructor() {
    this.dsn = process.env.SENTRY_DSN || '';
    this.environment = process.env.NODE_ENV || 'development';
    this.logger = Logger.getInstance({ name: 'SentryService' });
  }

  public static getInstance(): SentryService {
    if (!SentryService.instance) {
      SentryService.instance = new SentryService();
    }
    return SentryService.instance;
  }

  public initialize(): void {
    if (this.initialized) return;

    if (!this.dsn) {
      this.logger.warn('DSN do Sentry não configurado', {
        environment: this.environment,
      });
      return;
    }

    const envConfig = CONFIG[this.environment] || CONFIG.development;

    try {
      this.logger.info('Inicializando Sentry', {
        environment: this.environment,
      });

      Sentry.init({
        dsn: this.dsn,
        environment: this.environment,
        debug: envConfig.debug,
        tracesSampleRate: envConfig.tracesSampleRate,
        profilesSampleRate: envConfig.profilesSampleRate,
        maxBreadcrumbs: 50,
        attachStacktrace: true,
        maxValueLength: 1000,
        integrations: [nodeProfilingIntegration()],
      });

      this.setupGlobalHandlers();
      this.initialized = true;
      this.logger.info(
        `Sentry inicializado com sucesso no ambiente: ${this.environment}`
      );
    } catch (error) {
      this.logger.error('Erro na inicialização do Sentry:', error);
    }
  }

  public configureApp(app: Application): void {
    if (!this.initialized) return;

    // The request handler must be the first middleware
    app.use(Handlers.requestHandler());

    // TracingHandler creates a trace for every incoming request
    app.use(Handlers.tracingHandler());
    app.use(Handlers.tracingHandler());
    // Add context enrichment middleware
    app.use((req: Request, res: Response, next: NextFunction) => {
      Sentry.configureScope((scope) => {
        scope.setTag('method', req.method);
        scope.setTag('path', req.path);
        scope.setTag('status_code', res.statusCode.toString());
      });
      next();
    });

    // The error handler must be registered before any other error middleware and after all controllers
    app.use(
      Handlers.errorHandler({
        shouldHandleError(error: Error & { status?: number }) {
          return error.status === undefined || error.status >= 400;
        },
      })
    );

    this.logger.info('Middleware do Sentry configurado com sucesso');
  }

  private setupGlobalHandlers(): void {
    process.on('uncaughtException', (error: Error) => {
      this.logger.error('Erro não tratado:', error);
      captureException(error);
      process.exit(1);
    });

    process.on('unhandledRejection', (reason: unknown) => {
      const error =
        reason instanceof Error ? reason : new Error(String(reason));
      this.logger.error('Rejeição não tratada:', error);
      captureException(error);
    });
  }
}

export default SentryService;
function captureException(_error: Error) {
  throw new Error('Function not implemented.');
}
