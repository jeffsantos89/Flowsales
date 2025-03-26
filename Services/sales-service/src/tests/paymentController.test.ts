version: '3.8'

services:
  sales-service:
    build: .
    environment:
      - PORT=5000
      - DB_HOST=postgres
      - DB_USER=postgres
      - DB_PASS=postgres
      - DB_NAME=flowsale_sales
    depends_on:
      - postgres
    ports:
      - '5000:5000'

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - '5432:5432'

  redis:
    image: redis:alpine
    ports:
      - '6379:6379'
