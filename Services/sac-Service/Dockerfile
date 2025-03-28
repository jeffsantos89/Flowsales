# Etapa de build
FROM node:18-alpine AS builder

# Definindo diretório de trabalho
WORKDIR /app

# Copiando arquivos de dependências
COPY package*.json ./

# Instalando dependências
RUN npm ci --only=production

# Copiando o restante dos arquivos
COPY . .

# Rodando o build
RUN npm run build

# Etapa final
FROM node:18-alpine

# Definindo diretório de trabalho
WORKDIR /app

# Copiando arquivos necessários da etapa de build
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json .

# Definindo variáveis de ambiente
ENV NODE_ENV=production
ENV PORT=4000

# Expondo a porta
EXPOSE $PORT

# Comando para rodar a aplicação
CMD ["node", "dist/index.js"]
