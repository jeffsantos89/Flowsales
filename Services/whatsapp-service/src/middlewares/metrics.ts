import { Request, Response, NextFunction } from 'express';
import client from 'prom-client';

const collectDefaultMetrics = client.collectDefaultMetrics;
collectDefaultMetrics();

const httpRequestDurationMicroseconds = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duração das requisições HTTP em segundos',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.1, 0.3, 0.5, 1, 1.5]
});

export const metricsMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const end = httpRequestDurationMicroseconds.startTimer();
  res.on('finish', () => {
    end({ route: req.path, method: req.method, status: res.statusCode });
  });
  next();
};

export const metricsEndpoint = (req: Request, res: Response) => {
  res.set('Content-Type', client.register.contentType);
  res.end(client.register.metrics());
};
