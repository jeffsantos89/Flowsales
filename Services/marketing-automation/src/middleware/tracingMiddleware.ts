import { trace } from '@opentelemetry/api';

export const tracingMiddleware = (req, res, next) => {
  const span = trace.getTracer('default').startSpan(`HTTP ${req.method} ${req.url}`);
  res.on('finish', () => span.end());
  next();
};
