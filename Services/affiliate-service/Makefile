SHELL := /bin/bash

ENV ?= dev
PORT ?= 3000

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	npm install && npm run test

lint:
	npm run lint

build:
	docker build -t affiliate-service .

dev:
	npm install && npm run dev

ci:
	npm ci && npm run lint && npm test