
# 🏗️ Page Builder Service — Flowsales

Cria páginas de vendas e automação, com um editor drag-and-drop e suporte a A/B testing.

## 🚀 Tecnologias

- Node.js / TypeScript
- PostgreSQL + Redis
- JWT, Rate Limiter
- Observabilidade (Prometheus, Grafana, OpenTelemetry)
- Docker, Helm, CI/CD

## 🛠️ Comandos

- `make dev` - roda localmente com hot reload
- `make test` - executa testes
- `make lint` - valida código
- `make build` - cria a imagem Docker

## 🔐 Segurança

- JWT assinado
- Rate limiter e CORS
- `.env.example` separa variáveis por ambiente

## 📊 Observabilidade

- Exposição de métricas via /metrics
- Integração com Grafana e Prometheus
