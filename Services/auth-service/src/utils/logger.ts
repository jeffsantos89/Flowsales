import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import path from 'path';

// Import the module to extend winston.transports

class Logger {
    private static instance: Logger;
    private logger: winston.Logger;

    private constructor() {
        const logDir = 'logs';
        const logFormat = winston.format.combine(
            winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
            winston.format.errors({ stack: true }),
            winston.format.splat(),
            winston.format.json()
        );

        this.logger = winston.createLogger({
            level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
            format: logFormat,
            defaultMeta: { service: 'auth-service' },
            transports: [
                // Console transport for development
                new winston.transports.Console({
                    format: winston.format.combine(
                        winston.format.colorize(),
                        winston.format.simple()
                    ),
                }),
                // Rotating file transport for production
                new DailyRotateFile({
                    filename: path.join(logDir, 'error-%DATE%.log'),
                    datePattern: 'YYYY-MM-DD',
                    zippedArchive: true,
                    maxSize: '20m',
                    maxFiles: '14d',
                    level: 'error'
                }),
                new DailyRotateFile({
                    filename: path.join(logDir, 'combined-%DATE%.log'),
                    datePattern: 'YYYY-MM-DD',
                    zippedArchive: true,
                    maxSize: '20m',
                    maxFiles: '14d',
                }),
            ],
            exceptionHandlers: [
                new DailyRotateFile({
                    filename: path.join(logDir, 'exceptions-%DATE%.log'),
                    datePattern: 'YYYY-MM-DD',
                    zippedArchive: true,
                    maxSize: '20m',
                    maxFiles: '14d',
                }),
            ],
            rejectionHandlers: [
                new DailyRotateFile({
                    filename: path.join(logDir, 'rejections-%DATE%.log'),
                    datePattern: 'YYYY-MM-DD',
                    zippedArchive: true,
                    maxSize: '20m',
                    maxFiles: '14d',
                }),
            ],
        });
    }

    public static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }

    public info(message: string, meta?: any): void {
        this.logger.info(message, meta);
    }

    public error(message: string, error?: Error | any): void {
        this.logger.error(message, { error: error?.stack || error });
    }

    public warn(message: string, meta?: any): void {
        this.logger.warn(message, meta);
    }

    public debug(message: string, meta?: any): void {
        this.logger.debug(message, meta);
    }

    public http(message: string, meta?: any): void {
        this.logger.http(message, meta);
    }
}

// Export a singleton instance
export const logger = Logger.getInstance();