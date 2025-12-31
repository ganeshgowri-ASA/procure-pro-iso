# Procure-Pro-ISO Makefile
# Common commands for development and deployment

.PHONY: help install dev test migrate seed setup run clean

# Default target
help:
	@echo "Procure-Pro-ISO - Available Commands"
	@echo "====================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make setup        - Run full database setup (migrate + seed)"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database schema migration"
	@echo "  make seed         - Insert seed data"
	@echo "  make db-status    - Show database status"
	@echo "  make db-test      - Test database connection"
	@echo "  make db-reset     - Reset database (DROPS ALL DATA)"
	@echo ""
	@echo "Alembic Migrations:"
	@echo "  make alembic-revision MSG='description' - Create new migration"
	@echo "  make alembic-upgrade  - Apply pending migrations"
	@echo "  make alembic-downgrade - Rollback one migration"
	@echo "  make alembic-history  - Show migration history"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Start development server"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove cached files"

# Install dependencies
install:
	pip install -r requirements.txt

# Run full database setup
setup:
	python scripts/setup.py

# Run schema migration only
migrate:
	python -m database.migration_runner migrate

# Insert seed data
seed:
	python -m database.migration_runner seed

# Show database status
db-status:
	python -m database.migration_runner status

# Test database connection
db-test:
	python scripts/test_connection.py

# Reset database (dangerous!)
db-reset:
	python -m database.migration_runner reset

# Create new Alembic migration
alembic-revision:
	alembic revision --autogenerate -m "$(MSG)"

# Apply pending Alembic migrations
alembic-upgrade:
	alembic upgrade head

# Rollback one Alembic migration
alembic-downgrade:
	alembic downgrade -1

# Show Alembic migration history
alembic-history:
	alembic history

# Start development server
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest tests/ -v

# Run linter
lint:
	ruff check .

# Clean cached files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
