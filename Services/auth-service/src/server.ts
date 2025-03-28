import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import authRoutes from './api/routes/auth';
import logger from './logger';
import { errorHandler } from './middleware/errorHandler';
import { requestLogger } from './middleware/requestLogger';

dotenv.config();

class Server {
    private readonly app: Application;
    private readonly port: number;
    private static instance: Server;

    private constructor() {
        this.app = express();
        this.port = this.normalizePort(process.env.PORT || '3001');
        this.setupMiddleware();
        this.setupRoutes();
        this.setupErrorHandling();
    }

    public static getInstance(): Server {
        if (!Server.instance) {
            Server.instance = new Server();
        }
        return Server.instance;
    }

    private normalizePort(val: string): number {
        const port = parseInt(val, 10);
        if (isNaN(port)) {
            throw new Error('Invalid port configuration');
        }
        return port;
    }

    private setupMiddleware(): void {
        // Security middleware
        this.app.use(helmet());
        this.app.use(cors({
            origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
            credentials: true
        }));

        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutes
            max: 100 // limit each IP to 100 requests per windowMs
        });
        this.app.use(limiter);

        // Utility middleware
        this.app.use(compression());
        this.app.use(express.json({ limit: '10kb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10kb' }));
        this.app.use(requestLogger);
    }

    private setupRoutes(): void {
        // API routes
        this.app.use('/api/v1/auth', authRoutes);
        
        // Health check route
        this.app.get('/health', (_: Request, res: Response) => {
            res.status(200).json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime()
            });
        });

        // Handle 404
        this.app.use('*', (_: Request, res: Response) => {
            res.status(404).json({ error: 'Resource not found' });
        });
    }

    private setupErrorHandling(): void {
        this.app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
            errorHandler(err, req, res, next);
        });
    }

    public async start(): Promise<void> {
        try {
            await new Promise<void>((resolve) => {
                this.app.listen(this.port, () => {
                    logger.info(`🚀 Auth service running on port ${this.port}`);
                    logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
                    resolve();
                });
            });

            this.setupProcessHandlers();
        } catch (error) {
            logger.error('Failed to start server:', error);
            process.exit(1);
        }
    }

    private setupProcessHandlers(): void {
        // Graceful shutdown
        const gracefulShutdown = (signal: string) => {
            logger.info(`Received ${signal}. Graceful shutdown initiated...`);
            process.exit(0);
        };

        // Process handlers
        process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
        process.on('SIGINT', () => gracefulShutdown('SIGINT'));
        process.on('unhandledRejection', (error: Error) => {
            logger.error('Unhandled Rejection:', error);
        });
        process.on('uncaughtException', (error: Error) => {
            logger.error('Uncaught Exception:', error);
            process.exit(1);
        });
    }

    public getApp(): Application {
        return this.app;
    }
}

// Initialize and start server
if (require.main === module) {
    const server = Server.getInstance();
    server.start().catch((error) => {
        logger.error('Server startup failed:', error);
        process.exit(1);
    });
}

export default Server;
