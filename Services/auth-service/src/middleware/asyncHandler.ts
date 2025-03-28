import { Request, Response, NextFunction, RequestHandler } from 'express';

// Tipos mais específicos
interface AsyncHandlerOptions {
    handleError?: boolean;
    timeout?: number;
    enableLogging?: boolean;
}

interface StandardError {
    status: number;
    message: string;
    stack?: string;
    timestamp: string;
    path: string;
    method: string;
    code?: string;
}

class RequestTimeoutError extends Error {
    constructor(timeout: number) {
        super(`Request timeout after ${timeout}ms`);
        this.name = 'RequestTimeoutError';
    }
}

/**
 * Creates a wrapper for async route handlers with built-in error handling and timeout control
 * @param fn The async route handler function
 * @param options Configuration options for the async handler
 * @returns Express middleware function
 */
const asyncHandler = (
    fn: (req: Request, res: Response, next: NextFunction) => Promise<any>,
    options: AsyncHandlerOptions = {}
): RequestHandler => {
    // Default options com destructuring
    const {
        handleError = true,
        timeout = 30000,
        enableLogging = true
    } = options;

    const createTimeoutPromise = (ms: number): Promise<never> => {
        return new Promise((_, reject) => {
            const timeoutId = setTimeout(() => {
                clearTimeout(timeoutId);
                reject(new RequestTimeoutError(ms));
            }, ms);
        });
    };

    const formatError = (error: any, req: Request): StandardError => ({
        status: error.status || 500,
        message: error.message || 'Internal Server Error',
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
        timestamp: new Date().toISOString(),
        path: req.path,
        method: req.method,
        code: error.code
    });

    const logError = (error: StandardError, req: Request): void => {
        if (!enableLogging) return;

        console.error('[AsyncHandler Error]:', {
            error,
            requestId: req.headers['x-request-id'],
            userId: req.headers['user-id'],
            ip: req.ip,
            userAgent: req.headers['user-agent']
        });
    };

    const sendErrorResponse = (res: Response, error: StandardError): void => {
        if (res.headersSent) return;

        res.status(error.status).json({
            error: {
                message: error.message,
                code: error.code,
                ...(process.env.NODE_ENV === 'development' && { stack: error.stack }),
                timestamp: error.timestamp
            }
        });
    };

    return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
        try {
            const result = await Promise.race([
                fn(req, res, next),
                createTimeoutPromise(timeout)
            ]);

            if (!res.headersSent && result !== undefined) {
                res.json(result);
            }
        } catch (error) {
            if (handleError) {
                const standardError = formatError(error, req);
                logError(standardError, req);
                sendErrorResponse(res, standardError);
            } else {
                next(error);
            }
        }
    };
};

export default asyncHandler;