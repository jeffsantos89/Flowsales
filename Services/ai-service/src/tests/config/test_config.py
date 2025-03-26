import os

# Configuração global para ambiente de teste
os.environ["TEST_MODE"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET"] = "testsecret"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["CACHE_TTL"] = "3600"
os.environ["API_RATE_LIMIT"] = "100"
os.environ["MAX_CONNECTIONS"] = "50"
os.environ["TIMEOUT"] = "30"
os.environ["SSL_VERIFY"] = "True"
os.environ["API_VERSION"] = "v1"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,http://localhost:8080"
os.environ["SENTRY_DSN"] = "https://test@sentry.io/123456"
os.environ["METRICS_ENABLED"] = "True"
os.environ["TRACING_ENABLED"] = "True"