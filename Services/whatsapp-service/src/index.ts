import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import authRoutes from './routes/authRoutes';
import userRoutes from './routes/userRoutes';
import messageRoutes from './routes/messageRoutes';
import metricsRoutes from './routes/metricsRoutes';
import { AppDataSource } from './config/db';
import { rateLimitMiddleware } from './middlewares/rateLimitMiddleware';
import { requestLogger } from './middlewares/requestLogger';
import { errorHandler } from './middlewares/errorHandler';

class App {
  listen() {
    throw new Error('Method not implemented.');
  }
  private app: Application;
  private readonly PORT: number;

  constructor() {
    this.app = express();
    this.PORT = Number(process.env.PORT) || 3000;
    this.setupMiddlewares();
    this.setupRoutes();
    this.setupErrorHandling();
  }

  private setupMiddlewares(): void {
    this.app.use(helmet()); // Adds security headers
    this.app.use(cors());
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
    this.app.use(morgan('dev')); // Request logging
    this.app.use(requestLogger);
    this.app.use(rateLimitMiddleware);
  }

  private setupRoutes(): void {
    this.app.use('/api/auth', authRoutes);
    this.app.use('/api/users', userRoutes);
    this.app.use('/api/messages', messageRoutes);
    this.app.use('/api/metrics', metricsRoutes);
  }

  private setupErrorHandling(): void {
    this.app.use(errorHandler);
  }

  public start(): void {
    this.app.listen(this.PORT, () => {
      console.log(`Server is running on port ${this.PORT}`);
    });
  }
}

const appInstance = new App();
appInstance.start();

export default appInstance;