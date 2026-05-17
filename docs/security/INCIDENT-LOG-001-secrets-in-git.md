# Incident Log #001 — Secrets em git history

**Data de identificação**: 2026-05-16
**Severidade**: P0 (débito técnico, não incidente ativo)
**Status do repo no momento**: Privado, sem clones externos, sem produção
**Risco real atual**: Baixo
**Risco futuro se não corrigir**: Alto (vai pra staging/prod com débito; impede abertura de portfolio público)

---

## Resumo Executivo

20 arquivos `.env*` rastreados pelo git (git ls-files). Dos 20:
- 5 contêm secrets **CRÍTICOS** (valores hardcoded fracos como `supersecret`, `admin123`)
- 8 contêm secrets de **PROVIDER** com formato reconhecível (maioria PLACEHOLDER)
- 7 são puramente CONFIG (URLs locais, feature flags, portas) — baixo risco

3 K8s secret YAMLs com valores base64 (`my-secret-key`, `postgres`) — decodificados e classificados.

**Resultado da triagem**: Nenhum secret REAL_DEV encontrado. Todos os valores de provider são claramente placeholders (`SEU_TOKEN_AQUI`, `app_id`, `app_secret`, `SUA_CHAVE_DO_MERCADO_PAGO`). Rotação nos painéis dos providers **não é obrigatória** — não há evidência de chaves de API reais.

Porém, secrets de categoria CRÍTICO (JWT, encryption keys) **devem ser rotacionados localmente** mesmo sendo "dev" — higiene e princípio.

---

## Inventário Completo

### CRÍTICO — Rotação obrigatória local

| Arquivo | Variável | Valor | Ação |
|---------|---------|-------|------|
| `Services/affiliate-service/.env.affiliate` | `JWT_SECRET` | `supersecret` | Rotacionar |
| `Services/affiliate-service/.env.affiliate` | `JWT_SECRET` (bloco duplicado) | `mysecretkey` | Rotacionar |
| `Services/affiliate-service/.env.affiliate` | `ENCRYPTION_KEY` | `32charlongencryptionkey1234567` | Rotacionar |
| `Services/affiliate-service/.env.affiliate` | `ENCRYPTION_KEY` (bloco duplicado) | `myencryptionkey32bytes` | Rotacionar |
| `Services/affiliate-service/.env.affiliate` | `REDIS_PASSWORD` | `senha-segura-redis` | Rotacionar |
| `Services/voip-service/.env.voip` | `AUTH_PASS` | `admin123` | Rotacionar |
| `Services/voip-service/.env.voip` | `ARI_PASS` | `my_super_secret_password` | Rotacionar |
| `Services/whatsapp-service/.env.whatsapp` | `JWT_SECRET` | `supersecretkey` | Rotacionar |
| `Services/store-service/.env.store` | `JWT_SECRET` | `minha_chave_jwt` | Rotacionar |
| `Services/marketing-service/.env.marketing` | `JWT_SECRET` | `sua_chave_jwt_supersecreta` | Rotacionar |
| `Services/integrations-service/.env.integrations` | `JWT_SECRET` | `sua_chave_jwt` | Rotacionar |
| `Infra/kubernetes/jwt-secret.yaml` | `jwt-secret` | `my-secret-key` (base64) | Rotacionar |
| `Services/sales-service/.env.sales` | `JWT_SECRET` | `your_jwt_secret_key` | Rotacionar |

### PROVIDER — Verificar e classificar

| Arquivo | Variável | Valor | Classificação |
|---------|---------|-------|--------------|
| `Services/affiliate-service/.env.affiliate` | `SENTRY_DSN` | `https://sentry.io/123456` | PLACEHOLDER (URL inválida) |
| `Services/affiliate-service/.env.affiliate` | `AWS_ACCESS_KEY_ID` | `your_access_key_id` | PLACEHOLDER |
| `Services/affiliate-service/.env.affiliate` | `AWS_SECRET_ACCESS_KEY` | `your_secret_access_key` | PLACEHOLDER |
| `Services/affiliate-service/.env.affiliate` | `ZABBIX_API_TOKEN` | `seu_token_aqui` | PLACEHOLDER |
| `Services/whatsapp-service/.env.whatsapp` | `WHATSAPP_API_TOKEN` | `SEU_TOKEN_AQUI` | PLACEHOLDER |
| `Services/whatsapp-service/.env.whatsapp` | `WHATSAPP_PHONE_NUMBER_ID` | `SEU_PHONE_ID_AQUI` | PLACEHOLDER |
| `Services/payment-service/.env.paymant` | `MERCADO_PAGO_ACCESS_TOKEN` | `SUA_CHAVE_DO_MERCADO_PAGO` | PLACEHOLDER |
| `Services/integrations-service/.env.integrations` | `FACEBOOK_APP_ID` | `app_id` | PLACEHOLDER |
| `Services/integrations-service/.env.integrations` | `FACEBOOK_APP_SECRET` | `app_secret` | PLACEHOLDER |
| `Services/integrations-service/.env.integrations` | `TWILIO_ACCOUNT_SID` | `sid` | PLACEHOLDER |
| `Services/integrations-service/.env.integrations` | `TWILIO_AUTH_TOKEN` | `token` | PLACEHOLDER |
| `Services/sales-service/.env.sales` | `STRIPE_API_KEY` | `my-stripe-key` | PLACEHOLDER |
| `Services/sales-service/.env.sales` | `TWILIO_ACCOUNT_SID` | `my-twilio-sid` | PLACEHOLDER |
| `Services/sales-service/.env.sales` | `TWILIO_AUTH_TOKEN` | `my-twilio-token` | PLACEHOLDER |
| `Services/marketing-service/.env.marketing` | `EMAIL_PASS` | `sua_senha` | PLACEHOLDER |
| `Mobile/.env.mobile` | `API_URL` | `https://store.example.com` | PLACEHOLDER (domínio fake) |

**Conclusão PROVIDER: todos são PLACEHOLDER. Nenhuma chave de API real encontrada. Revogação em painéis externos não é necessária.**

### CONFIG — Sem ação de segurança necessária (mover para .env.example)

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| `Services/crm-service/.env.crm` | Deletado no git status (D) | Já resolvido no git |
| `Services/leads-service/.env.leads` | Deletado no git status (D) | Já resolvido no git |
| `Services/marketing-automation/.env.automation` | Portas, URLs locais, `NODE_ENV` | CONFIG puro |
| `Frontend/.env.front` | URLs de API locais, feature flags | CONFIG puro |
| `Services/finance-service/.env.example` | Arquivo `.example` — rastreado OK | Permitido pelo gitignore |
| `Services/integrations/.env.example` | Pasta integrations/ legada | Verificar necessidade |
| `Services/page-builder-service/.env.example` | Arquivo `.example` — OK | Permitido |
| `Services/pixel-service/.env.example` | Arquivo `.example` — OK | Permitido |
| `Services/reporting-service/.env.example` | Arquivo `.example` — OK | Permitido |
| `Services/team-management-service/.env.example` | Arquivo `.example` — OK | Permitido |

### K8s Secrets — Classificação

| Arquivo | Valor decodificado | Classificação |
|---------|------------------|--------------|
| `Infra/kubernetes/db-secret.yaml` | username=postgres, password=postgres | CRÍTICO (credencial de DB, mesmo que fraca) |
| `Infra/kubernetes/jwt-secret.yaml` | jwt-secret=my-secret-key | CRÍTICO (JWT secret comprometido) |
| `Infra/kubernetes/secrets.yaml` | username=postgres, password=postgres, database=flowsale | CRÍTICO (credencial de DB) |

---

## Arqueologia Git

| Item | Valor |
|------|-------|
| Total de commits com .env | 2 |
| Autores | Jeferson Santos |
| Primeiro commit | `44a0ab153` — "Commit inicial do projeto Flowsale" (2025-03-26) |
| Último commit | `74d4fbaca` — "aprimoramento fronte e crm" (2025-03-28) |
| Branches afetadas | main (único branch com 2 commits afetados) |
| Exposição externa | ZERO — repo privado, sem clones, sem CI/CD externo |

---

## Decisão sobre reescrita de histórico

**Recomendação: SIM, reescrever histórico com git-filter-repo.**

Justificativa:
- Repo privado ✅
- Apenas 2 commits afetados ✅
- Único autor ✅
- Zero clones externos ✅
- Zero usuários reais ✅
- Nenhuma tag de release publicada externamente ✅
- Desejo futuro de portfolio público ou staging ✅

Benefício: histórico completamente limpo, git clone fresh nunca terá acesso a esses dados.

---

## Plano de Remediação

| Etapa | Ação | Prompt | Status |
|-------|------|--------|--------|
| 1 | ✅ Inventário (este documento) | FIX-1 | ✅ Concluído |
| 2 | Cleanup tracking + reescrita histórico + hooks | FIX-2 | ⏳ Aguardando confirmação |
| 3 | Secrets fortes locais + .env.example padronizados | FIX-3 | ⏳ |
| 4 | Consumer faltante da saga (sales → finance) | FIX-4 | ⏳ |
| 5 | Re-audit confirmando resolução | FIX-5 | ⏳ |

---

## Secrets a Rotacionar (checklist local)

### Críticos — Gerar novos com `openssl rand -base64 64`
- [ ] JWT_SECRET — affiliate-service
- [ ] ENCRYPTION_KEY — affiliate-service
- [ ] JWT_SECRET — whatsapp-service
- [ ] JWT_SECRET — store-service
- [ ] JWT_SECRET — marketing-service
- [ ] JWT_SECRET — integrations-service
- [ ] JWT_SECRET — sales-service
- [ ] AUTH_PASS — voip-service
- [ ] ARI_PASS — voip-service
- [ ] jwt-secret — K8s (Infra/kubernetes/jwt-secret.yaml)
- [ ] DB password — K8s (Infra/kubernetes/db-secret.yaml, secrets.yaml)

### Providers — Nenhuma ação necessária
Todos os valores de provider confirmados como PLACEHOLDER. Não há chaves de API reais no histórico.

---

## Pergunta ao usuário antes do FIX-2

> O FIX-2 vai:
> 1. Fazer backup completo do repo (mirror)
> 2. `git rm --cached` em todos os `.env` com secrets reais
> 3. Reescrever histórico com `git filter-repo` (remove os 2 commits problemáticos do histórico)
> 4. Force push na main
> 5. Instalar husky + gitleaks pre-commit hook
> 6. Criar GitHub Action de security scan
>
> **Confirma que pode prosseguir?** Histórico dos 2 commits afetados será reescrito (irreversível sem o backup).
