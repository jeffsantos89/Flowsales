SHELL := /bin/bash

run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v --disable-warnings

lint:
	ruff --fix src/

format:
	black src/

build:
	docker build -t ai-service .

logs:
	docker-compose logs -f ai-service