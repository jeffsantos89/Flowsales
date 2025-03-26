import winston from 'winston';
import LogstashTransport = require('winston-logstash-transport');
import { Request } from 'express';
import logstashConfig from '../config/logstashConfig';

interface LogMetadata {
  correlationId?: string;
  serviceName?: string;
  environment?: string;
  timestamp?: string;
  [key: string]: unknown;
}

class Logger {
  private static instance: Logger;
  private logger: winston.Logger;
  private readonly serviceName: string = 'affiliate-service';

  private constructor() {
    const { combine, timestamp, json, colorize, printf, errors } =
      winston.format;

    const productionFormat = combine(
      errors({ stack: true }),
      timestamp(),
      json()
    );

    const developmentFormat = printf(
      ({ level, message, timestamp, ...metadata }) => {
        return `[${timestamp}] ${level.toUpperCase()}: ${message} ${
          Object.keys(metadata).length ? JSON.stringify(metadata, null, 2) : ''
        }`;
      }
    );

    this.logger = winston.createLogger({
      level: process.env.LOG_LEVEL || logstashConfig.level || 'info',
      defaultMeta: {
        service: this.serviceName,
        environment: process.env.NODE_ENV,
      },
      format:
        process.env.NODE_ENV === 'production'
          ? productionFormat
          : combine(timestamp(), json()),
      transports: [
        new LogstashTransport({
          host: logstashConfig.host,
          port: logstashConfig.port || 5044,
          ssl_enable: logstashConfig.ssl || false,
          max_connect_retries: logstashConfig.maxRetries || 5,
          timeout_connect: 3000,
          timeout: 5000,
        }),
      ],
      exitOnError: false,
    });

    if (process.env.NODE_ENV !== 'production') {
      this.logger.add(
        new winston.transports.Console({
          format: combine(colorize(), timestamp(), developmentFormat),
        })
      );
    }
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private formatMessage(
    message: string | object,
    metadata?: LogMetadata
  ): [string, LogMetadata] {
    const formattedMetadata = {
      timestamp: new Date().toISOString(),
      ...metadata,
    };

    const formattedMessage =
      typeof message === 'string' ? message : JSON.stringify(message);

    return [formattedMessage, formattedMetadata];
  }

  public error(message: string | object, metadata?: LogMetadata): void {
    const [msg, meta] = this.formatMessage(message, metadata);
    this.logger.error(msg, meta);
  }

  public warn(message: string | object, metadata?: LogMetadata): void {
    const [msg, meta] = this.formatMessage(message, metadata);
    this.logger.warn(msg, meta);
  }

  public info(message: string | object, metadata?: LogMetadata): void {
    const [msg, meta] = this.formatMessage(message, metadata);
    this.logger.info(msg, meta);
  }

  public debug(message: string | object, metadata?: LogMetadata): void {
    const [msg, meta] = this.formatMessage(message, metadata);
    this.logger.debug(msg, meta);
  }

  public logWithContext(
    req: Request,
    message: string | object,
    level: 'error' | 'warn' | 'info' | 'debug' = 'info'
  ): void {
    const metadata: LogMetadata = {
      correlationId: (req.headers['x-correlation-id'] as string) || 'no-id',
      requestId: req.headers['x-request-id'] as string,
      userId: req.headers['x-user-id'] as string,
      path: req.path,
      method: req.method,
    };

    switch (level) {
      case 'error':
        this.error(message, metadata);
        break;
      case 'warn':
        this.warn(message, metadata);
        break;
      case 'debug':
        this.debug(message, metadata);
        break;
      default:
        this.info(message, metadata);
    }
  }
}

export const logger = Logger.getInstance();
export default logger;
