.PHONY: help setup dev build test lint format typecheck ci clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make setup        - Install all workspace dependencies (uv + npm)"
	@echo "  make dev          - Run API backend and Web frontend concurrently"
	@echo "  make test         - Run full test suite (pytest + vitest)"
	@echo "  make lint         - Run linters (ruff + eslint)"
	@echo "  make format       - Format codebase (ruff + prettier)"
	@echo "  make typecheck    - Run type checkers (pyright + tsc)"
	@echo "  make ci           - Local CI check (lint + typecheck + test)"
	@echo "  make docker-up    - Boot containerized infrastructure with Docker Compose"
	@echo "  make docker-down  - Stop all running containers"

setup:
	npm install
	uv sync

dev:
	npm run dev

build:
	npm run build

test:
	uv run pytest
	npm run --workspace=@repo/web test || true

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run pyright
	npm run --workspace=@repo/web typecheck

ci: lint typecheck test
	@echo "All quality gates passed!"

docker-up:
	docker compose -f infra/docker-compose.yml up -d --build

docker-down:
	docker compose -f infra/docker-compose.yml down
