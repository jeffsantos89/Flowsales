// src/logs/logService.ts
import { createLogger, transports, format } from 'winston';

const logger = createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
  transports: [
    new transports.Console(),
    new transports.File({ filename: './logs/app.log' }),
  ],
});

export const logInfo = (message: string) => logger.info(message);
export const logError = (message: string) => logger.error(message);
