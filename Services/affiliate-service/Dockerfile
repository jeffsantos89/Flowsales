# 🛠️ Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app

# Copia apenas arquivos essenciais para o build (melhora cache de build)
COPY package*.json tsconfig.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# 🛠️ Stage 2: Production
FROM node:18-alpine
WORKDIR /app

# Configuração de Segurança (Usuário não root)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copia os artefatos do build
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

# Copia certificados SSL/TLS para mTLS (autenticação mútua)
COPY certs/client-cert.pem certs/client-key.pem certs/ca-cert.pem /app/certs/

# Configuração de segurança adicional
RUN chown -R appuser:appgroup /app && \
    chmod -R 755 /app

USER appuser

# Exposição da porta
EXPOSE 4000

# Healthcheck para garantir disponibilidade do container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f https://localhost:4000/health || exit 1

# Comando para iniciar o serviço
CMD ["node", "dist/app.js"]

