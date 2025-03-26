import { Request, Response, NextFunction } from 'express';
import { randomUUID } from 'crypto';
import { validate as isUUID } from 'uuid';

interface CorrelationIdOptions {
    headerKey?: string;
    validateUUID?: boolean;
    allowEmpty?: boolean;
    maxLength?: number;
}

const DEFAULT_OPTIONS: Required<CorrelationIdOptions> = {
    headerKey: 'x-correlation-id',
    validateUUID: true,
    allowEmpty: false,
    maxLength: 128
};

export class CorrelationIdMiddleware {
    private readonly options: Required<CorrelationIdOptions>;

    constructor(options: CorrelationIdOptions = {}) {
        this.options = { ...DEFAULT_OPTIONS, ...options };
    }

    private validateCorrelationId(correlationId: string): boolean {
        if (!correlationId && !this.options.allowEmpty) {
            return false;
        }

        if (correlationId.length > this.options.maxLength) {
            return false;
        }

        if (this.options.validateUUID && !isUUID(correlationId)) {
            return false;
        }

        return true;
    }

    public handle = (req: Request, res: Response, next: NextFunction): void => {
        try {
            const incomingCorrelationId = req.headers[this.options.headerKey.toLowerCase()] as string;
            const correlationId = incomingCorrelationId || randomUUID();

            if (!this.validateCorrelationId(correlationId)) {
                const newCorrelationId = randomUUID();
                req.correlationId = newCorrelationId;
                res.setHeader(this.options.headerKey, newCorrelationId);
            } else {
                req.correlationId = correlationId;
                res.setHeader(this.options.headerKey, correlationId);
            }
            next();
        } catch (error) {
            next(error);
        }
    };
