# 🛒 Store Service — Flowsales

Gerencia catálogo, estoque e integrações de marketplace.

## 🚀 Tecnologias

- Node.js / TypeScript
- PostgreSQL + Redis
- JWT + Headers seguros
- Prometheus, Grafana, OpenTelemetry
- Docker + Helm + Makefile

## ⚙️ Comandos

- `make dev` - roda localmente
- `make test` - roda testes
- `make lint` - valida código

## 🔐 Segurança

- JWT assinado
- Rate limiter e CORS configuráveis
- Headers e ambientes separados via `.env.example`

## 📊 Observabilidade

- Exposição de métricas via `/metrics`
- Integração com Prometheus e Grafana