# 💬 WhatsApp Service — Flowsales

Gerencia mensagens, envio automático e integração com a API oficial do WhatsApp Business.

## 🚀 Tecnologias

- Node.js / TypeScript
- PostgreSQL + Redis
- JWT, CORS, Headers seguros
- Observabilidade com Prometheus, Grafana, OpenTelemetry
- Docker + Helm + CI/CD

## ⚙️ Comandos

- `make dev` - roda localmente
- `make test` - roda testes
- `make lint` - valida código

## 🔐 Segurança

- JWT centralizado
- Rate limiter, CORS, headers seguros
- `.env.example` separado por ambiente

## 📊 Observabilidade

- Exporta métricas via `/metrics`
- Pronto para Prometheus + Grafana