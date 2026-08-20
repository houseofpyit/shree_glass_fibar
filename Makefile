.PHONY: help build up down restart logs shell db-shell migrate seed test lint format

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker commands
build: ## Build Docker containers
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## View application logs
	docker compose logs -f app

logs-all: ## View all service logs
	docker compose logs -f

shell: ## Open shell in app container
	docker compose exec app bash

db-shell: ## Open PostgreSQL shell
	docker compose exec db psql -U postgres -d shreeglass

# Database commands
migrate: ## Run database migrations
	docker compose exec app alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	docker compose exec app alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Rollback last migration
	docker compose exec app alembic downgrade -1

seed: ## Seed database with sample data
	docker compose exec app python scripts/seed.py

# Development
dev: ## Run development server locally (requires venv)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	docker compose exec app pytest tests/ -v

lint: ## Run linter
	docker compose exec app python -m py_compile app/main.py

# Production
prod-up: ## Start production services
	docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

prod-down: ## Stop production services
	docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml down

# Backup
backup-db: ## Backup PostgreSQL database
	docker compose exec db pg_dump -U postgres shreeglass > backup_$$(date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore PostgreSQL database (usage: make restore-db file=backup.sql)
	cat $(file) | docker compose exec -T db psql -U postgres -d shreeglass
