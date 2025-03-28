import { Request, Response, NextFunction } from 'express';
import { ValidationError as ExpressValidatorError } from 'express-validator';

interface ValidationError {
    path: string;
    msg: string;
    value: any;
    location?: string;
    type?: string;
    nestedErrors?: ValidationError[];
}
import { logger } from '../utils/logger';
import { StatusCodes } from 'http-status-codes';

// Enhanced error types with descriptions
export enum ErrorType {
    VALIDATION = 'ValidationError',
    BUSINESS = 'BusinessError',
    TECHNICAL = 'TechnicalError',
    AUTHENTICATION = 'AuthenticationError',
    AUTHORIZATION = 'AuthorizationError',
    NETWORK = 'NetworkError',
    DATABASE = 'DatabaseError',
    EXTERNAL_SERVICE = 'ExternalServiceError'
}

// Enhanced error response interface
interface IErrorDetail {
    field?: string;
    message: string;
    value?: unknown;
    code?: string;
}

interface IErrorResponse {
    success: false;
    error: {
        message: string;
        type: ErrorType;
        code: number;
        timestamp: string;
        path: string;
        details?: IErrorDetail[];
        stack?: string;
        correlationId?: string;
    };
}

// Enhanced AppError with better context handling
export class AppError extends Error {
    public readonly timestamp: Date;
    public readonly correlationId?: string;

    constructor(
        public readonly statusCode: number,
        public readonly message: string,
        public readonly type: ErrorType = ErrorType.TECHNICAL,
        public readonly source?: string,
        public readonly isOperational = true,
        public readonly context: Record<string, unknown> = {},
        correlationId?: string
    ) {
        super(message);
        this.timestamp = new Date();
        this.correlationId = correlationId;
        Object.setPrototypeOf(this, AppError.prototype);
        Error.captureStackTrace(this, this.constructor);
    }

    public toJSON(): Record<string, unknown> {
        return {
            message: this.message,
            type: this.type,
            statusCode: this.statusCode,
            timestamp: this.timestamp.toISOString(),
            source: this.source,
            context: this.context,
            correlationId: this.correlationId,
            stack: process.env.NODE_ENV === 'development' ? this.stack : undefined
        };
    }
}

// Request context extractor with sanitization
const extractRequestContext = (req: Request): Record<string, unknown> => {
    const sensitiveFields = ['password', 'token', 'apiKey'];
    const sanitizedBody = { ...req.body };
    const sanitizedQuery = { ...req.query };

    sensitiveFields.forEach(field => {
        if (field in sanitizedBody) sanitizedBody[field] = '[REDACTED]';
        if (field in sanitizedQuery) sanitizedQuery[field] = '[REDACTED]';
    });

    return {
        path: req.path,
        method: req.method,
        body: sanitizedBody,
        query: sanitizedQuery,
        params: req.params,
        ip: req.ip,
        userAgent: req.headers['user-agent'],
        correlationId: req.headers['x-correlation-id'] || crypto.randomUUID()
    };
};

// Type guard for express-validator array
function isExpressValidatorArray(
    errors: Error | AppError | ValidationError[]
): errors is ValidationError[] {
    return (
        Array.isArray(errors) &&
        errors.length > 0 &&
        'msg' in errors[0]
    );
}

// Error mapper utility
const mapError = (err: Error | AppError | ValidationError[]): {
    statusCode: number;
    message: string;
    type: ErrorType;
    details?: IErrorDetail[];
} => {
    if (err instanceof AppError) {
        return {
            statusCode: err.statusCode,
            message: err.message,
            type: err.type
        };
    }

    if (err instanceof SyntaxError) {
        return {
            statusCode: StatusCodes.BAD_REQUEST,
            message: 'Invalid JSON payload',
            type: ErrorType.VALIDATION
        };
    }

    if (isExpressValidatorArray(err)) {
        return {
            statusCode: StatusCodes.UNPROCESSABLE_ENTITY,
            message: 'Validation Error',
            type: ErrorType.VALIDATION,
            details: err.map(e => ({
                field: e.path,
                message: e.msg,
                value: e.value
            }))
        };
    }
    if (err instanceof Error && 'code' in err) {
        if (err.code === 'ECONNREFUSED') {
            return {
                statusCode: StatusCodes.SERVICE_UNAVAILABLE,
                message: 'Service temporarily unavailable',
                type: ErrorType.NETWORK
            };
        }
    }
    return {
        statusCode: StatusCodes.INTERNAL_SERVER_ERROR,
        message: 'Internal Server Error',
        type: ErrorType.TECHNICAL
    };
};

// Enhanced error handler middleware
export const errorHandler = (
    err: Error | AppError | ValidationError[],
    req: Request,
    res: Response,
    next: NextFunction
): Response => {
    const requestContext = extractRequestContext(req);
    const { statusCode, message, type, details } = mapError(err);

    // Log error with context
    logger.error('Error occurred while processing request', {
        error: err instanceof AppError ? err.toJSON() : err,
        context: requestContext
    });

    const errorResponse: IErrorResponse = {
        success: false,
        error: {
            message,
            type,
            code: statusCode,
            timestamp: new Date().toISOString(),
            path: req.originalUrl,
            correlationId: requestContext.correlationId as string,
            ...(details && { details }),
            ...(process.env.NODE_ENV === 'development' && !Array.isArray(err) && { stack: err.stack })
        }
    };

    return res.status(statusCode).json(errorResponse);
};

// Enhanced not found handler
export const notFoundHandler = (req: Request, res: Response): Response => {
    const context = extractRequestContext(req);
    const error = new AppError(
        StatusCodes.NOT_FOUND,
        'Resource not found',
        ErrorType.TECHNICAL,
        req.originalUrl,
        true,
        {},
        context.correlationId as string
    );

    return errorHandler(error, req, res, () => null);
};

// Enhanced async handler with better typing and error boundary
export const asyncHandler = <T>(
    fn: (req: Request, res: Response, next: NextFunction) => Promise<T>
) => {
    return (req: Request, res: Response, next: NextFunction): Promise<void> => {
        return Promise.resolve(fn(req, res, next)).then(() => {}).catch(error => {
            if (error instanceof Error) {
                next(error);
            } else {
                next(new AppError(
                    StatusCodes.INTERNAL_SERVER_ERROR,
                    'Unknown error occurred',
                    ErrorType.TECHNICAL
                ));
            }
        });
    };
};
