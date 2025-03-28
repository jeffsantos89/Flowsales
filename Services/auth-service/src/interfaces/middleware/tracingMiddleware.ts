import { trace } from '@opentelemetry/api';

export const tracingMiddleware = (req, res, next) => {
  const span = trace.getTracer('default').startSpan(\`\${req.method} \${req.url}\`);
  res.on('finish', () => span.end());
  next();
};
