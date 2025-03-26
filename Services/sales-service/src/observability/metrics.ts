import { register, Histogram, Gauge } from 'prom-client';

export const requestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duração das requisições HTTP em segundos',
  labelNames: ['method', 'route', 'status_code'],
});

export const activeUsers = new Gauge({
  name: 'active_users',
  help: 'Número de usuários ativos',
});
