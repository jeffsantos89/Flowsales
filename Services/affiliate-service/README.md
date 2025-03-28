# 🧩 Affiliate Service — Flowsales

Este microserviço é responsável pelo gerenciamento de afiliados, comissionamentos e performance de vendas da plataforma Flowsales.

---

## 🔧 Tecnologias Utilizadas

- Node.js / TypeScript
- Docker / Docker Compose
- PostgreSQL / Redis
- CI/CD via GitHub Actions
- Prometheus, Grafana, Zabbix
- mTLS, WAF, Istio
- Testes: Jest + Supertest (E2E e Integração)

---

## 🚀 Comandos Úteis

```bash
# Subir ambiente local
docker-compose up -d --build

# Rodar testes
npm install
npm run test

# Lint
npm run lint
```

---

## 🔐 Segurança

- Comunicação segura via mTLS (Istio + WAF)
- Autenticação planejada com JWT + Redis
- Políticas por ambiente com ConfigMap/Secrets
- Separação entre ambientes dev / staging / prod

---

## 📈 Observabilidade

- Prometheus com dashboard de métricas
- Grafana já configurado no painel
- Exporters e sidecars no `docker-compose.yaml`

---

## 📦 Estrutura

```
src/
├── controllers/
├── services/
├── middleware/
├── routes/
├── models/
├── utils/
├── tests/
│   ├── integration/
│   └── e2e/
config/
security/
.github/
```

---

## 🛠️ Melhorias Futuras

- Refatorar autenticação para padrão JWT universal
- Aplicar rate limiter com Redis ou memory
- Consolidar métricas diretamente no código
- Adicionar Circuit Breaker com fallback resiliente

---