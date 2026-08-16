.PHONY: help up down build logs backend-shell frontend-shell test test-unit test-api test-integration lint migrate migrate-new

help:
	@echo "AskMyDocs AI — common commands"
	@echo "  make up               Start all services via docker compose"
	@echo "  make down             Stop all services"
	@echo "  make build            Rebuild images"
	@echo "  make logs             Tail logs for all services"
	@echo "  make test             Run unit + API tests (backend)"
	@echo "  make test-integration Run integration tests (needs db running)"
	@echo "  make lint             Run backend + frontend linters"
	@echo "  make migrate          Apply DB migrations"
	@echo "  make migrate-new msg=\"add table\"  Create a new migration"

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

backend-shell:
	docker compose exec backend bash

frontend-shell:
	docker compose exec frontend sh

test:
	cd backend && pytest -m "unit or api"

test-unit:
	cd backend && pytest -m unit

test-api:
	cd backend && pytest -m api

test-integration:
	cd backend && pytest -m integration

lint:
	cd backend && ruff check app tests
	cd frontend && npm run lint

migrate:
	docker compose exec backend alembic upgrade head

migrate-new:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"
