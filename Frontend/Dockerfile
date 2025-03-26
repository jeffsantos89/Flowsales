# Etapa 1: build
FROM node:18-alpine AS builder

# Defina variáveis de ambiente para melhorar a segurança
ENV NODE_ENV=production

WORKDIR /app

# Copie apenas os arquivos necessários para instalar as dependências
COPY package.json package-lock.json ./

# Instale as dependências com cache para melhorar a eficiência
RUN npm ci --only=production

# Copie o restante do código
COPY . .

# Execute o build da aplicação
RUN npm run build

# Etapa 2: Servir no Nginx
FROM nginx:stable-alpine

# Remova arquivos desnecessários para reduzir a imagem final
RUN rm -rf /usr/share/nginx/html/*

# Copie os arquivos buildados da etapa anterior
COPY --from=builder /app/build /usr/share/nginx/html

# Copie uma configuração customizada do Nginx, se necessário
# COPY nginx.conf /etc/nginx/nginx.conf

# Defina um usuário não root para rodar o Nginx, melhorando a segurança
RUN adduser -D -g 'www' www && \
    chown -R www:www /usr/share/nginx/html

USER www

# Exponha a porta 80
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]
