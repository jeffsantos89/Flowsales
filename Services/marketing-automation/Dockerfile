# Etapa 1: Build
FROM node:18-alpine AS build
WORKDIR /app

# Copiar apenas os arquivos necessários para instalar as dependências
COPY package*.json ./
RUN npm install --frozen-lockfile

# Copiar o restante dos arquivos e construir o projeto
COPY . .
RUN npm run build

# Etapa 2: Produção
FROM node:18-alpine
WORKDIR /app

# Copiar apenas os arquivos necessários para a produção
COPY --from=builder /app/dist ./dist
COPY package*.json ./

# Instalar apenas as dependências de produção
RUN npm ci --only=production --frozen-lockfile

# Definir variáveis de ambiente
ENV NODE_ENV=production
ENV PORT=3000

# Expor a porta da aplicação
EXPOSE $PORT

# Comando para iniciar a aplicação
CMD ["node", "dist/index.js"]
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --production=false
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
RUN npm install --production
EXPOSE 3000
CMD ["node", "dist/index.js"]
