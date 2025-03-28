# 🔌 Integrations Service — Flowsales

Gerencia integrações com sistemas externos: Hotmart, Mercado Livre, Shopee, Facebook, etc.

## 🚀 Tecnologias

- Node.js / TypeScript
- PostgreSQL + Redis
- JWT, Rate Limiter
- Prometheus, OpenTelemetry, Grafana
- Docker, Helm, CI/CD

## 🛠️ Comandos

- `make dev` - roda localmente
- `make test` - executa testes
- `make lint` - valida padrões
- `make build` - gera imagem Docker

## 🔐 Segurança

- JWT assinado
- Headers seguros
- Rate limiter configurável
- `.env.example` por ambiente

## 📈 Observabilidade

- Exporta métricas via /metrics
- Pronto para dashboards Prometheus + Grafana