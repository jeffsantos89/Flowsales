from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

# Criando Rate Limiter para controlar requisições
limiter = Limiter(key_func=get_remote_address)

async def rate_limit_check(request: Request):
    """ Middleware para limitar número de requisições """
    try:
        limiter.check(request)
    except Exception:
        raise HTTPException(status_code=429, detail="Muitas requisições. Tente novamente mais tarde.")
        # Implementar backoff exponencial
        await limiter.update_rate(request)
        
        # Adicionar headers informativos na resposta
        request.state.rate_limit_remaining = limiter.get_window_stats(request)[1]
        request.state.rate_limit_reset = limiter.get_window_stats(request)[2]
        
        # Logging de tentativas de abuso
        if limiter.get_window_stats(request)[1] < 3:
            logger.warning(f"Rate limit quase excedido para IP {request.client.host}")
            
        # Permitir bypass para IPs confiáveis
        if request.client.host in settings.TRUSTED_IPS:
            return
            
        # Cache dos resultados para melhorar performance
        cache_key = f"ratelimit:{request.client.host}"
        if await cache.exists(cache_key):
            return
        await cache.set(cache_key, "1", expire=60)