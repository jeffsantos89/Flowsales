# 💸 Sales Service — Flowsales

Gerencia vendas, comissões, rastreamento de performance e geração de relatórios.

## 🚀 Tecnologias

- Node.js / TypeScript
- PostgreSQL + Redis
- JWT, Rate Limiter
- Prometheus, OpenTelemetry, Grafana
- Docker, Helm, CI/CD

## 🛠️ Comandos

- `make dev` - roda localmente
- `make test` - executa testes
- `make lint` - valida código
- `make build` - cria imagem Docker

## 🔐 Segurança

- JWT assinado
- Rate limiter e CORS
- `.env.example` separado por ambiente

## 📊 Observabilidade

- Exposição de métricas via /metrics
- Integração com Grafana e Prometheus