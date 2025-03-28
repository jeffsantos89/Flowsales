import { Router, Request, Response } from 'express';
import { celebrate, Joi, Segments } from 'celebrate';
import { loginHandler } from '../../controllers/authController';
import rateLimit from 'express-rate-limit';
import asyncHandler from '../../middleware/asyncHandler';
import { version } from '../../../package.json';

// Constants
const RATE_LIMIT = {
    WINDOW_MS: 15 * 60 * 1000, // 15 minutes
    MAX_ATTEMPTS: 5,
    BLOCKED_MESSAGE: 'Too many login attempts. Please try again later.'
};

// Rate limiting configuration with more options
const loginLimiter = rateLimit({
    windowMs: RATE_LIMIT.WINDOW_MS,
    max: RATE_LIMIT.MAX_ATTEMPTS,
    message: RATE_LIMIT.BLOCKED_MESSAGE,
    standardHeaders: true,
    legacyHeaders: false,
    skipSuccessfulRequests: true, // Don't count successful logins
    keyGenerator: (req) => req.ip || req.socket.remoteAddress || 'unknown' // Ensure we always return a string
});

// Validation schema with more strict rules
const loginValidation = celebrate({
    [Segments.BODY]: Joi.object({
        email: Joi.string()
            .email()
            .required()
            .trim()
            .lowercase()
            .max(255),
        password: Joi.string()
            .required()
            .min(8)
            .max(100)
            .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$/)
            .messages({
                'string.pattern.base': 'Password must contain at least one uppercase letter, one lowercase letter, one number and one special character'
            })
    }).options({ stripUnknown: true })
});

class AuthRouter {
    private router: Router;

    constructor() {
        this.router = Router();
        this.initializeRoutes();
    }

    private initializeRoutes(): void {
        // Auth routes
        this.router.post(
            '/login',
            loginLimiter,
            loginValidation,
            asyncHandler(loginHandler)
        );

        // Health check with more detailed response
        this.router.get('/health', (_req: Request, res: Response): void => {
            const healthCheck = {
                status: 'ok',
                timestamp: new Date(),
                service: 'auth-service',
                version: version || '1.0.0'
            };
            res.status(200).json(healthCheck);
        });
    }

    public getRouter(): Router {
        return this.router;
    }
}

export default new AuthRouter().getRouter();
