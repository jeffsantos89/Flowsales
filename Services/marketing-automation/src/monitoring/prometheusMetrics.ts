// src/monitoring/prometheusMetrics.ts
import client from 'prom-client';

const register = new client.Registry();

const httpRequestDurationMicroseconds = new client.Histogram({
  name: 'http_request_duration_ms',
  help: 'Duration of HTTP requests in ms',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [50, 100, 200, 300, 400, 500, 1000],
});

register.registerMetric(httpRequestDurationMicroseconds);
client.collectDefaultMetrics({ register });

export { httpRequestDurationMicroseconds, register };
