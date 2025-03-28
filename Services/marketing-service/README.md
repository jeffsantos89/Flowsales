# 📣 Marketing Service — Flowsales

Microserviço responsável por campanhas, tracking, automações e fluxos de marketing.

## 🔧 Tecnologias

- Node.js / TypeScript
- PostgreSQL + Redis
- Docker + Compose
- JWT + CORS
- Observabilidade com Prometheus + OpenTelemetry

## 🛠️ Scripts

- `make dev` - roda localmente
- `make test` - roda testes
- `make lint` - valida padrões

## 🔐 Segurança

- JWT centralizado
- Rate limiting (opcional via Redis)
- Header validation
- `.env.example` para separar ambientes

## 📈 Observabilidade

- Exposição de métricas via /metrics
- Integração pronta com Grafana e Prometheus