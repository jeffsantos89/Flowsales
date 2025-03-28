# 🔌 Integrations-Service — Flowsales

Responsável pelo consumo de webhooks, orquestração e sincronização entre parceiros da plataforma.

## 🚀 Tecnologias

- Node.js / TypeScript
- PostgreSQL, Redis, Webhooks
- JWT, Rate Limiter
- Docker, Makefile, CI/CD
- Observabilidade com Prometheus + Grafana

## ⚙️ Comandos

- `make dev` - roda localmente
- `make test` - executa testes
- `make lint` - valida estilo
- `make build` - cria imagem Docker

## 🔐 Segurança

- JWT assinado
- Rate limiter e CORS
- `.env.example` com separação por ambiente

## 📊 Observabilidade

- Exposição de métricas via `/metrics`
- Integração com Grafana e Prometheus