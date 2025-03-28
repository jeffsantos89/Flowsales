
# 💰 Finance Service — Flowsales

Gerencia planos de assinatura, billing, faturas e controle financeiro da plataforma.

## 🚀 Tecnologias

- Node.js / TypeScript
- PostgreSQL + Redis
- JWT, Rate Limiter
- Observabilidade (Prometheus, OpenTelemetry, Grafana)
- Docker, Helm, CI/CD

## 🛠️ Comandos

- `make dev` - roda localmente
- `make test` - executa testes
- `make lint` - valida estilo de código
- `make build` - gera imagem Docker

## 🔐 Segurança

- JWT assinado
- Rate limiter e CORS
- `.env.example` com variáveis separadas

## 📊 Observabilidade

- Exposição de métricas via /metrics
- Integração com Grafana e Prometheus
