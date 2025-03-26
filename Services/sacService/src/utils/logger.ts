import { createLogger, format, transports, Logger } from 'winston';
import 'winston-daily-rotate-file';
import * as path from 'path';

const logDir = path.join(__dirname, '../../logs');

const dailyRotateFileTransport = new transports.DailyRotateFile({
  filename: `${logDir}/%DATE%-sac-service.log`,
  datePattern: 'YYYY-MM-DD',
  zippedArchive: true,
  maxSize: '20m',
  maxFiles: '14d'
});

const consoleTransport = new transports.Console({
  format: format.combine(
    format.colorize(),
    format.printf(({ timestamp, level, message }) => {
      return `${timestamp} [${level}]: ${message}`;
    })
  )
});

export const logger: Logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.splat(),
    format.json()
  ),
  transports: [
    dailyRotateFileTransport,
    consoleTransport
  ],
  exceptionHandlers: [
    new transports.File({ filename: `${logDir}/exceptions.log` })
  ],
  rejectionHandlers: [
    new transports.File({ filename: `${logDir}/rejections.log` })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new transports.Console({
    format: format.simple()
  }));
}

