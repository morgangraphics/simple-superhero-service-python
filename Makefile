.DEFAULT_GOAL := help

# ─── Virtual environment ──────────────────────────────────────────────────────

.venv:
	uv venv .venv --python 3.12

install: .venv  ## Install all dependencies (including dev)
	uv sync --extra dev

# ─── Service ──────────────────────────────────────────────────────────────────

start: ## Start the service (foreground)
	uv run python main.py

dev: ## Start the service with auto-reload
	uv run uvicorn service:create_app --factory --reload --host 127.0.0.1 --port 8000

stop: ## Stop any background uvicorn process
	@pkill -f "uvicorn service:create_app" && echo "Service stopped." || echo "No running service found."

# ─── Tests ────────────────────────────────────────────────────────────────────

test: ## Run all unit tests
	uv run pytest unit/

test-unit: ## Run unit tests (alias)
	uv run pytest unit/

test-file: ## Run file utility tests only
	uv run pytest unit/test_file.py -s

test-verbose: ## Run unit tests with verbose output
	uv run pytest unit/ -v

# ─── Coverage ─────────────────────────────────────────────────────────────────

coverage: ## Run tests with coverage report (terminal)
	uv run coverage erase
	uv run coverage run -m pytest unit/
	uv run coverage report --show-missing

coverage-html: ## Run tests with coverage report (HTML)
	uv run coverage erase
	uv run coverage run -m pytest unit/
	uv run coverage html
	@echo "Report available at htmlcov/index.html"

# ─── Code quality ─────────────────────────────────────────────────────────────

lint: ## Run ruff linter
	uv run ruff check .

lint-fix: ## Run ruff linter and auto-fix
	uv run ruff check . --fix

format: ## Run black formatter
	uv run black .

format-check: ## Check formatting without making changes
	uv run black . --check

# ─── SSL certs ────────────────────────────────────────────────────────────────

certs: ## Generate self-signed SSL certs for local development
	openssl req -x509 -newkey rsa:4096 -keyout sssp-key.pem -out sssp-cert.pem \
		-days 365 -nodes -subj "/CN=localhost"

# ─── Docker ───────────────────────────────────────────────────────────────────

IMAGE ?= simple-superhero-service-python

docker-build: ## Build the Docker image
	docker build -t $(IMAGE) .

docker-start: ## Run the container (mounts local certs, exposes port 8000)
	docker run --rm -p 8000:8000 \
		-v $(PWD)/sssp-cert.pem:/home/appuser/service/sssp-cert.pem:ro \
		-v $(PWD)/sssp-key.pem:/home/appuser/service/sssp-key.pem:ro \
		-v $(PWD)/config/.env:/home/appuser/service/config/.env:ro \
		$(IMAGE)

docker-stop: ## Stop the running container
	@docker stop $$(docker ps -q --filter ancestor=$(IMAGE)) 2>/dev/null && echo "Container stopped." || echo "No running container found."

docker-shell: ## Open a shell in a new container
	docker run --rm -it $(IMAGE) /bin/bash

# ─── Help ─────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install start dev stop test test-unit test-file test-verbose \
        coverage coverage-html lint lint-fix format format-check certs \
        docker-build docker-start docker-stop docker-shell help
