#!/bin/bash
echo "🧹 Limpando cache do Redis..."
redis-cli -h $REDIS_HOST FLUSHALL
echo "✅ Cache limpo!"
# Definir variáveis de ambiente
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"

# Função para validar conexão
check_redis_connection() {
    if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
        echo "❌ Erro: Não foi possível conectar ao Redis em $REDIS_HOST:$REDIS_PORT"
        exit 1
    fi
}

# Função para limpar cache com autenticação
clear_redis_cache() {
    local auth_params=""
    if [ -n "$REDIS_PASSWORD" ]; then
        auth_params="-a $REDIS_PASSWORD"
    fi
    
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" $auth_params FLUSHALL; then
        echo "✅ Cache limpo com sucesso!"
    else
        echo "❌ Erro ao limpar o cache"
        exit 1
    fi
}

# Execução principal
check_redis_connection
clear_redis_cache