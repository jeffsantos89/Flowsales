SHELL := /bin/bash

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

dev:
	npm install && npm run dev

build:
	docker build -t sac-service .

test:
	npm run test

lint:
	npm run lint