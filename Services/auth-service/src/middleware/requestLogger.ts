import { Request, Response, NextFunction } from 'express';
import winston from 'winston';
import { v4 as uuidv4 } from 'uuid';
import os from 'os';

// Custom interface for extended request
interface ExtendedRequest extends Request {
    requestId?: string;
    startTime?: [number, number];
}

// Configure Winston logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json(),
        winston.format.prettyPrint()
    ),
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' }),
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.simple()
            ),
        }),
    ],
});

// Request Logger Configuration
const config = {
    excludePaths: ['/health', '/metrics'],
    maskSensitiveData: true,
    sensitiveFields: ['password', 'token', 'authorization', 'cookie'],
};

// Mask sensitive data in objects
const maskSensitiveData = (data: any): any => {
    if (!data) return data;
    const masked = { ...data };
    
    Object.keys(masked).forEach(key => {
        if (config.sensitiveFields.includes(key.toLowerCase())) {
            masked[key] = '********';
        } else if (typeof masked[key] === 'object') {
            masked[key] = maskSensitiveData(masked[key]);
        }
    });
    
    return masked;
};

// Main request logger middleware
export const requestLogger = (req: ExtendedRequest, res: Response, next: NextFunction): void => {
    // Skip logging for excluded paths
    if (config.excludePaths.includes(req.path)) {
        return next();
    }

    // Generate unique request ID
    req.requestId = uuidv4();
    req.startTime = process.hrtime();

    // Capture original end function
    const originalEnd = res.end;
    
    // Override end function to log response
    res.end = function(this: Response, ...args: any[]): Response {
        const duration = process.hrtime(req.startTime as [number, number]);
        const durationInMs = (duration[0] * 1000 + duration[1] / 1e6).toFixed(2);

        const logData = {
            requestId: req.requestId,
            timestamp: new Date().toISOString(),
            method: req.method,
            path: req.path,
            query: config.maskSensitiveData ? maskSensitiveData(req.query) : req.query,
            body: config.maskSensitiveData ? maskSensitiveData(req.body) : req.body,
            statusCode: res.statusCode,
            responseTime: `${durationInMs}ms`,
            userAgent: req.get('user-agent'),
            ip: req.ip,
            hostname: os.hostname(),
            correlationId: req.get('x-correlation-id'),
        };

        // Log based on status code
        if (res.statusCode >= 500) {
            logger.error('Request failed', logData);
        } else if (res.statusCode >= 400) {
            logger.warn('Request warning', logData);
        } else {
            logger.info('Request completed', logData);
        }

        // Add response headers
        res.setHeader('X-Request-ID', req.requestId || '');
        res.setHeader('X-Response-Time', `${durationInMs}ms`);

        // Call original end function
        return originalEnd.apply(this, args);
    };

    // Error handling
    const errorHandler = (error: Error): void => {
        logger.error('Request error', {
            requestId: req.requestId,
            error: {
                message: error.message,
                stack: error.stack,
            },
        });
    };

    req.on('error', errorHandler);
    res.on('error', errorHandler);

    next();
};

export default requestLogger;