import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { createNamespace } from 'cls-hooked';
import { Logger } from 'winston';

// Criação de um namespace para o contexto de rastreamento
const traceNamespace = createNamespace('trace');

// Função para configurar o logger (exemplo usando winston)
const configureLogger = (): Logger => {
    const { createLogger, format, transports } = require('winston');
    return createLogger({
        level: 'info',
        format: format.combine(
            format.timestamp(),
            format.json()
        ),
        transports: [
            new transports.Console(),
            // Adicione outros transports conforme necessário (ex: arquivos, serviços externos)
        ],
    });
};

const logger = configureLogger();

export const traceMiddleware = (req: Request, res: Response, next: NextFunction) => {
    traceNamespace.run(() => {
        try {
            const traceId = req.headers['x-trace-id'] as string || uuidv4();
            req.headers['x-trace-id'] = traceId;
            res.setHeader('X-Trace-Id', traceId);

            // Armazenar o traceId no contexto
            traceNamespace.set('traceId', traceId);

            // Log do início da requisição
            logger.info(`Request received`, { traceId, method: req.method, url: req.url });

            // Log do fim da requisição
            res.on('finish', () => {
                logger.info(`Request completed`, { traceId, method: req.method, url: req.url, statusCode: res.statusCode });
            });

            next();
        } catch (error) {
            logger.error('Error in traceMiddleware', { error });
            next(error);
        }
    });
};