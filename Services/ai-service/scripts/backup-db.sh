#!/bin/bash

# Habilita modo estrito de execução
set -euo pipefail
IFS=$'\n\t'

# Configurações
BACKUP_DIR="/backups"
RETENTION_DAYS=7
MAX_RETRIES=3
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/db-backup-${TIMESTAMP}.sql.gz"

# Função para log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Função para limpeza em caso de erro
cleanup() {
    if [ -f "$BACKUP_FILE" ]; then
        rm -f "$BACKUP_FILE"
        log "🧹 Arquivo de backup incompleto removido"
    fi
}

# Registra handler para trap de erros
trap cleanup ERR

# Verifica variáveis de ambiente necessárias
required_vars=("POSTGRES_USER" "POSTGRES_HOST" "POSTGRES_DB")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        log "❌ Erro: Variável de ambiente $var não definida"
        exit 1
    fi
done

# Verifica se diretório de backup existe
if [ ! -d "$BACKUP_DIR" ]; then
    log "📁 Criando diretório de backup..."
    mkdir -p "$BACKUP_DIR"
fi

# Tenta fazer o backup com retries
log "🚀 Iniciando backup do banco de dados..."
for ((i=1; i<=MAX_RETRIES; i++)); do
    if pg_dump -U "$POSTGRES_USER" -h "$POSTGRES_HOST" -d "$POSTGRES_DB" 2>/dev/null | gzip > "$BACKUP_FILE"; then
        log "✅ Backup completado com sucesso: $BACKUP_FILE"
        break
    else
        if [ $i -eq $MAX_RETRIES ]; then
            log "❌ Falha após $MAX_RETRIES tentativas"
            exit 1
        fi
        log "⚠️ Tentativa $i falhou, tentando novamente..."
        sleep 5
    fi
done

# Remove backups antigos
log "🧹 Removendo backups mais antigos que $RETENTION_DAYS dias..."
find "$BACKUP_DIR" -name "db-backup-*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Mostra tamanho do backup
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "📊 Tamanho do backup: $BACKUP_SIZE"
