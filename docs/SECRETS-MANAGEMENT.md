# Gestão de Segredos — Flowsale

## Princípios (invioláveis)

1. Segredos **NUNCA** em git, em qualquer ambiente
2. Segredos **NUNCA** hardcoded em código-fonte
3. Segredos **NUNCA** em logs, mesmo que parcialmente mascarados (usar `REDACTED`)
4. Segredos **NUNCA** em URLs como query params
5. Cada ambiente (dev/staging/prod) tem secrets **diferentes**
6. Rotação trimestral mínima em produção

---

## Por ambiente

### Dev local

- Cada dev tem seu próprio `.env` local (não versionado, no `.gitignore`)
- Bootstrap via `./scripts/setup-env.sh` — gera secrets aleatórios fortes via `openssl`
- Senhas fracas são OK para dev se o banco é local e inacessível externamente
- Providers externos: usar contas de sandbox/dev com chaves de teste

```bash
# Primeira vez ou novo clone:
./scripts/setup-env.sh

# Forçar regeneração (rotação de secrets dev):
./scripts/setup-env.sh --force

# Verificar quais serviços têm .env:
./scripts/setup-env.sh --check
```

### Staging

- Vault / AWS Secrets Manager (configurar antes de ir pra staging)
- Secrets injetados via Kubernetes ExternalSecrets Operator
- Rotação semestral
- Auditoria de acesso ativada

### Produção

- Mesmo Vault da staging, namespace separado
- Rotação trimestral obrigatória
- Acesso via JIT (just-in-time) com aprovação
- Audit log permanente
- Certificados via cert-manager + Let's Encrypt

---

## Como adicionar uma nova variável de ambiente

1. **NUNCA** edite `.env` diretamente esperando que vá pro git — está no `.gitignore`
2. Adicione a variável em `.env.example` do serviço com placeholder descritivo: `CHANGEME_NOME_DESCRITIVO`
3. Se for secret gerado localmente: adicione o pattern de substituição em `scripts/setup-env.sh`
4. Documente em quais ambientes é necessária e como gerar valor seguro
5. Se for secret de provider externo: documente em qual painel obter (ver seção abaixo)
6. Atualize o README do serviço com instruções de setup

---

## Providers externos — onde obter credenciais

| Provider | URL | Variável | Serviço |
|---------|-----|---------|--------|
| Focus NFe | https://focusnfe.com.br → Conta → API | `FOCUS_NFE_TOKEN` | finance-service |
| Asaas | https://sandbox.asaas.com → Conta → Chave de API | `ASAAS_API_KEY` | payment-service |
| Stripe | https://dashboard.stripe.com → Developers → API keys | `STRIPE_SECRET_KEY` | payment-service |
| Meta / WhatsApp | https://developers.facebook.com → Apps → WhatsApp | `WHATSAPP_API_TOKEN` | whatsapp-service |
| RD Station | https://appstore.rd.station → Meus apps | `RD_STATION_CLIENT_ID/SECRET` | integrations-service |
| HubSpot | https://developers.hubspot.com → Apps | `HUBSPOT_CLIENT_ID/SECRET` | integrations-service |
| Hotmart | https://developers.hotmart.com | `HOTMART_CLIENT_ID/SECRET` | integrations-service |
| Kiwify | https://api.kiwify.com.br | `KIWIFY_CLIENT_ID/SECRET` | integrations-service |
| ActiveCampaign | Conta → Settings → Developer → API | `ACTIVE_CAMPAIGN_API_URL/KEY` | integrations-service |
| Eduzz | https://api.eduzz.com → Credenciais | `EDUZZ_PUBLIC_KEY/PRIVATE_KEY` | integrations-service |
| OpenAI | https://platform.openai.com → API Keys | `OPENAI_API_KEY` | ai-service |

---

## Operações de rotação

### Rotacionar secret de serviço

```bash
# 1. Gerar novo secret seguro
openssl rand -base64 64  # para JWT secrets
openssl rand -hex 32     # para encryption keys / webhook secrets

# 2. Atualizar .env local (dev) ou Vault (staging/prod)
# 3. Reiniciar o serviço
# 4. Confirmar funcionamento nos logs
# 5. Documentar no CHANGELOG do serviço se for produção
```

### Secret de provider vazado

```
1. Revogar IMEDIATAMENTE no painel do provider (antes de investigar)
2. Gerar nova credencial no painel
3. Atualizar Vault / .env local
4. Reiniciar serviços afetados
5. Auditar logs procurando uso indevido da chave antiga
6. Documentar em docs/security/INCIDENT-LOG-{n}.md
7. Postmortem: como vazou, como prevenir
```

---

## Defesa em profundidade (camadas implementadas)

| Camada | Mecanismo | Status |
|--------|----------|--------|
| 1 | `.gitignore` — bloqueia tracking de `.env` | ✅ |
| 2 | Pre-commit hook (`.husky/pre-commit`) — bloqueia commit de `.env` e certs | ✅ |
| 3 | gitleaks — scan de secrets antes de cada commit | ✅ (hook) |
| 4 | GitHub Action `security-scan.yml` — gitleaks + Trivy + Snyk em todo push | ✅ |
| 5 | Trivy scan semanal programado | ✅ |
| 6 | Vault / Secrets Manager em staging/prod | 🔲 Pendente (próxima fase) |

---

## Regras de código

```typescript
// ❌ NUNCA: fallback hardcoded
const secret = process.env.JWT_SECRET || 'supersecret';

// ✅ CORRETO: falha explícita se variável ausente
const secret = process.env.JWT_SECRET;
if (!secret) throw new Error('JWT_SECRET env var is required');

// ✅ CORRETO: usando validação Zod no startup
const envSchema = z.object({
  JWT_SECRET: z.string().min(32, 'JWT_SECRET must be at least 32 chars'),
});
const env = envSchema.parse(process.env);
```

```python
# ❌ NUNCA
app.config['SECRET_KEY'] = 'supersecretkey'

# ✅ CORRETO
import os
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise RuntimeError('SECRET_KEY environment variable is required')
app.config['SECRET_KEY'] = secret_key
```
