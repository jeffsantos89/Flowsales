#!/usr/bin/env bash
# =============================================================================
# Flowsale — Bootstrap de variáveis de ambiente para desenvolvimento local
# =============================================================================
# Uso:
#   ./scripts/setup-env.sh           # cria .env de todos os serviços (skip se já existe)
#   ./scripts/setup-env.sh --force   # sobrescreve .env existentes
#   ./scripts/setup-env.sh --check   # apenas verifica se todos os .env existem
#
# Pré-requisito: openssl instalado (vem com Mac e Linux por padrão)
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORCE="${1:-}"
CHECK_ONLY="${1:-}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_err()  { echo -e "${RED}❌ $1${NC}"; }

# Verifica dependência
if ! command -v openssl >/dev/null 2>&1; then
  log_err "openssl não encontrado. Instale e tente novamente."
  exit 1
fi

# Geradores de secrets seguros
gen_base64()  { openssl rand -base64 "${1:-64}" | tr -d '\n='; }
gen_hex()     { openssl rand -hex "${1:-32}"; }
gen_password(){ openssl rand -base64 32 | tr -d '\n=/' | head -c 28; }

# Função principal: processa um serviço
process_service() {
  local example_file="$1"
  local env_file="$2"
  local label="$3"

  if [[ ! -f "$example_file" ]]; then
    log_warn "$label: .env.example não encontrado, skip"
    return
  fi

  if [[ "$CHECK_ONLY" == "--check" ]]; then
    if [[ -f "$env_file" ]]; then
      log_ok "$label: .env existe"
    else
      log_warn "$label: .env AUSENTE"
    fi
    return
  fi

  if [[ -f "$env_file" ]] && [[ "$FORCE" != "--force" ]]; then
    log_ok "$label: .env já existe (use --force para sobrescrever)"
    return
  fi

  cp "$example_file" "$env_file"

  # Substituições de secrets gerados aleatoriamente
  # Usa perl para compatibilidade Mac/Linux (sed -i tem comportamento diferente)
  local jwt_secret
  local db_pass
  local redis_pass
  local encryption_key
  local webhook_secret
  local admin_pass
  local pepper

  jwt_secret="$(gen_base64 64)"
  db_pass="$(gen_password)"
  redis_pass="$(gen_password)"
  encryption_key="$(gen_hex 32)"
  webhook_secret="$(gen_hex 32)"
  admin_pass="$(gen_password)"
  pepper="$(gen_hex 32)"

  perl -i -pe "
    s|CHANGEME_JWT_SECRET_64_CHARS|${jwt_secret}|g;
    s|CHANGEME_JWT_SECRET|${jwt_secret}|g;
    s|change-me-at-least-32-characters|${jwt_secret}|g;
    s|change-me-with-a-strong-secret|${jwt_secret}|g;
    s|CHANGEME_DB_PASSWORD|${db_pass}|g;
    s|CHANGEME_REDIS_PASSWORD|${redis_pass}|g;
    s|CHANGEME_32_BYTE_HEX_KEY_[0]{0,64}|${encryption_key}|g;
    s|CHANGEME_32_BYTE_HEX_KEY|${encryption_key}|g;
    s|CHANGEME_WEBHOOK_SECRET_HEX_32|${webhook_secret}|g;
    s|CHANGEME_WEBHOOK_SECRET|${webhook_secret}|g;
    s|CHANGEME_ADMIN_PASSWORD_STRONG|${admin_pass}|g;
    s|CHANGEME_HEX_64_CHARS_[0]{0,64}|${pepper}${pepper}|g;
    s|CHANGEME_HEX_[0-9]+_CHARS|${pepper}|g;
  " "$env_file"

  log_ok "$label: .env gerado com secrets fortes"
}

echo ""
echo "================================================="
echo "  Flowsale — Setup de variáveis de ambiente"
echo "================================================="
echo ""

if [[ "$CHECK_ONLY" == "--check" ]]; then
  echo "Modo: verificação apenas (sem criar/modificar arquivos)"
elif [[ "$FORCE" == "--force" ]]; then
  echo "Modo: --force (sobrescreve .env existentes)"
else
  echo "Modo: normal (skip se .env já existe; use --force para sobrescrever)"
fi
echo ""

# --- Serviços ---
declare -A SERVICES=(
  ["auth-service"]="Services/auth-service"
  ["crm-service"]="Services/crm-service"
  ["leads-service"]="Services/leads-service"
  ["sales-service"]="Services/sales-service"
  ["finance-service"]="Services/finance-service"
  ["payment-service"]="Services/payment-service"
  ["integrations-service"]="Services/integrations-service"
  ["affiliate-service"]="Services/affiliate-service"
  ["ai-service"]="Services/ai-service"
  ["marketing-automation"]="Services/marketing-automation"
  ["whatsapp-service"]="Services/whatsapp-service"
  ["sac-service"]="Services/sac-service"
  ["marketing-service"]="Services/marketing-service"
  ["store-service"]="Services/store-service"
  ["voip-service"]="Services/voip-service"
)

for service_name in "${!SERVICES[@]}"; do
  service_dir="${ROOT_DIR}/${SERVICES[$service_name]}"
  process_service \
    "${service_dir}/.env.example" \
    "${service_dir}/.env" \
    "$service_name"
done

# --- Frontend ---
process_service \
  "${ROOT_DIR}/Frontend/.env.example" \
  "${ROOT_DIR}/Frontend/.env.local" \
  "Frontend"

echo ""
echo "================================================="

if [[ "$CHECK_ONLY" == "--check" ]]; then
  echo "  Verificação concluída."
else
  echo "  Bootstrap concluído!"
  echo ""
  echo "  Próximos passos:"
  echo "  1. Preencha manualmente os valores de provider nos .env:"
  echo "     - FOCUS_NFE_TOKEN em finance-service"
  echo "     - ASAAS_API_KEY, STRIPE_SECRET_KEY em payment-service"
  echo "     - WHATSAPP_API_TOKEN em whatsapp-service"
  echo "     - OAuth clients em integrations-service"
  echo "     Ver docs/SECRETS-MANAGEMENT.md para guia completo"
  echo ""
  echo "  2. Subir infra local:"
  echo "     docker compose --profile core up -d"
  echo ""
  echo "  3. Rodar migrations:"
  echo "     pnpm -r migrate  (ou npm run migrate em cada serviço)"
  echo ""
  echo "  ⚠️  NUNCA commitar os .env gerados — estão protegidos pelo .gitignore e hooks"
fi
echo "================================================="
echo ""
