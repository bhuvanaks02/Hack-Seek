# HackSeek Development Makefile

.PHONY: help dev-setup dev-start dev-stop dev-logs dev-clean build test lint format

# Default target
help:
	@echo "HackSeek Development Commands:"
	@echo "  make dev-setup    - Set up development environment"
	@echo "  make dev-start    - Start development environment"
	@echo "  make dev-stop     - Stop development environment"
	@echo "  make dev-logs     - Show development logs"
	@echo "  make dev-clean    - Clean development environment"
	@echo "  make build        - Build all services"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Run linting on all code"
	@echo "  make format       - Format all code"
	@echo "  make db-reset     - Reset development database"
	@echo "  make scraper      - Start scraper service"
	@echo "  make admin        - Start PgAdmin"

# Development environment setup
dev-setup:
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file - please update with your API keys"; fi
	@mkdir -p database
	@docker-compose -f docker-compose.dev.yml build
	@echo "Development environment ready!"

# Start development environment
dev-start:
	@echo "Starting development environment..."
	@docker-compose -f docker-compose.dev.yml up -d postgres redis
	@echo "Waiting for database..."
	@sleep 10
	@docker-compose -f docker-compose.dev.yml up -d backend frontend
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"

# Stop development environment
dev-stop:
	@echo "Stopping development environment..."
	@docker-compose -f docker-compose.dev.yml down

# Show development logs
dev-logs:
	@docker-compose -f docker-compose.dev.yml logs -f

# Clean development environment
dev-clean:
	@echo "Cleaning development environment..."
	@docker-compose -f docker-compose.dev.yml down -v
	@docker system prune -f

# Build all services
build:
	@echo "Building all services..."
	@docker-compose -f docker-compose.dev.yml build

# Run tests
test:
	@echo "Running backend tests..."
	@docker-compose -f docker-compose.dev.yml exec backend pytest -v
	@echo "Running frontend tests..."
	@docker-compose -f docker-compose.dev.yml exec frontend npm test

# Run linting
lint:
	@echo "Running backend linting..."
	@docker-compose -f docker-compose.dev.yml exec backend flake8 .
	@docker-compose -f docker-compose.dev.yml exec backend mypy .
	@echo "Running frontend linting..."
	@docker-compose -f docker-compose.dev.yml exec frontend npm run lint

# Format code
format:
	@echo "Formatting backend code..."
	@docker-compose -f docker-compose.dev.yml exec backend black .
	@echo "Formatting frontend code..."
	@docker-compose -f docker-compose.dev.yml exec frontend npm run lint -- --fix

# Reset development database
db-reset:
	@echo "Resetting development database..."
	@docker-compose -f docker-compose.dev.yml stop postgres
	@docker-compose -f docker-compose.dev.yml rm -f postgres
	@docker volume rm hackseek_postgres_dev_data 2>/dev/null || true
	@docker-compose -f docker-compose.dev.yml up -d postgres
	@echo "Database reset complete!"

# Start scraper service
scraper:
	@echo "Starting scraper service..."
	@docker-compose -f docker-compose.dev.yml --profile scraper up -d scraper

# Start PgAdmin
admin:
	@echo "Starting PgAdmin..."
	@docker-compose -f docker-compose.dev.yml --profile admin up -d pgadmin
	@echo "PgAdmin available at: http://localhost:5050"
	@echo "Email: admin@hackseek.dev"
	@echo "Password: admin"