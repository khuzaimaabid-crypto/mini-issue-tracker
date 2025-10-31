.PHONY: help build up down restart logs clean test test-backend test-frontend setup

# Default target
help:
	@echo "Mini Issue Tracker - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup & Development:"
	@echo "  make setup          - Initial project setup"
	@echo "  make build          - Build Docker containers"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Logs & Monitoring:"
	@echo "  make logs           - View logs from all services"
	@echo "  make logs-backend   - View backend logs"
	@echo "  make logs-frontend  - View frontend logs"
	@echo "  make logs-db        - View database logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Run backend tests"
	@echo "  make test-frontend  - Run frontend tests"
	@echo ""
	@echo "Database:"
	@echo "  make db-shell       - Open PostgreSQL shell"
	@echo "  make db-backup      - Backup database"
	@echo "  make db-restore     - Restore database from backup"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make prune          - Clean up Docker system"
	@echo "  make shell-backend  - Open backend container shell"
	@echo "  make shell-frontend - Open frontend container shell"

# Setup
setup:
	@echo "Setting up project..."
	@chmod +x quick-start.sh
	@./quick-start.sh

# Build containers
build:
	docker-compose build

# Start services
up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Stop services
down:
	docker-compose down

# Restart services
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f db

# Run tests
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	docker-compose exec backend pytest tests/ -v

test-frontend:
	@echo "Running frontend tests..."
	docker-compose exec frontend npm test

# Database operations
db-shell:
	docker-compose exec db psql -U postgres -d issue_tracker

db-backup:
	@echo "Backing up database..."
	docker-compose exec db pg_dump -U postgres issue_tracker > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created!"

db-restore:
	@echo "Restoring database from backup.sql..."
	docker-compose exec -T db psql -U postgres issue_tracker < backup.sql
	@echo "Database restored!"

# Shell access
shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

# Cleanup
clean:
	docker-compose down -v
	@echo "Containers and volumes removed!"

prune:
	docker system prune -af --volumes
	@echo "Docker system cleaned!"

# Production deployment
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f