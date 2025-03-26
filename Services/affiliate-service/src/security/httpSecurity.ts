import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import { Request, Response } from 'express';

interface SecurityConfig {
    corsOrigins: string[];
    rateLimit: {
        windowMs: number;
        max: number;
    };
    enableHelmet: boolean;
}

// Default configuration
const DEFAULT_CONFIG: SecurityConfig = {
    corsOrigins: (process.env.CORS_ORIGINS || '').split(',').filter(Boolean),
    rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 100 // limit each IP to 100 requests per windowMs
    },
    enableHelmet: true
};

class SecurityMiddleware {
    private config: SecurityConfig;

    constructor(customConfig?: Partial<SecurityConfig>) {
        this.config = { ...DEFAULT_CONFIG, ...customConfig };
    }

    private corsErrorHandler(err: Error, req: Request, res: Response) {
        console.error(`CORS Error: ${err.message}`, {
            origin: req.headers.origin,
            path: req.path
        });
        return res.status(403).json({
            error: 'CORS Error',
            message: 'Origin not allowed'
        });
    }

    private createCorsMiddleware() {
        return cors({
            origin: (origin, callback) => {
                if (!origin || this.config.corsOrigins.includes(origin)) {
                    callback(null, true);
                } else {
                    callback(new Error(`Origin ${origin} not allowed by CORS`));
                }
            },
            credentials: true,
            optionsSuccessStatus: 200,
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            allowedHeaders: ['Content-Type', 'Authorization'],
            exposedHeaders: ['Content-Range', 'X-Content-Range'],
            preflightContinue: false,
            onError: this.corsErrorHandler
        });
    }

    private createRateLimitMiddleware() {
        return rateLimit({
            windowMs: this.config.rateLimit.windowMs,
            max: this.config.rateLimit.max
        });
    }

    private createHelmetMiddleware() {
        return helmet({
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'"],
                    scriptSrc: ["'self'", "'unsafe-inline'"],
                    styleSrc: ["'self'", "'unsafe-inline'"],
                    imgSrc: ["'self'", "data:", "https:"]
                }
            }
        });
    }

    public setupMiddleware(app: any) {
        if (this.config.enableHelmet) {
            app.use(this.createHelmetMiddleware());
        }
        app.use(this.createCorsMiddleware());
        app.use(this.createRateLimitMiddleware());
    }
