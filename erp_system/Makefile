.PHONY: help setup-local build docker up start-local down stop-local restart logs shell clean status test demo health all deep-clean

# Default target when running make
all: docker

# === LOCAL DEVELOPMENT (No Docker) ===
# Setup local environment and dependencies
setup-local:
	@echo "Setting up local development environment..."
	@echo "Creating virtual environment..."
	python3 -m venv .venv || true
	@echo "Installing dependencies..."
	.venv/bin/pip install -r requirements.txt
	@echo "Creating sample database..."
	.venv/bin/python create_sample_db.py || echo "Database already exists or will be created on first run"
	@echo "Local setup completed! Use 'make start-local'"

# Start locally (without Docker)
start-local:
	@echo "Starting ERP system locally..."
	@echo "Make sure you ran 'make setup-local' first"
	cd backend && ../.venv/bin/python api.py &
	sleep 3
	cd frontend && ../.venv/bin/python -m streamlit run streamlit_app.py --server.port=8501 &
	@echo "ERP system started locally!"
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend UI: http://localhost:8501"

# === DOCKER DEPLOYMENT (Recommended) ===
# Build the Docker containers
build:
	@echo "Building Docker containers..."
	docker compose build

# Start with Docker (recommended - no local setup needed)
docker: build
	docker compose up -d
	@echo "ERP system started with Docker!"
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend UI: http://localhost:8501"
	@echo "Note: Docker handles all dependencies automatically"

# Legacy alias for docker
up: docker

# Stop local processes
stop-local:
	pkill -f "python.*api.py" || true
	pkill -f "streamlit run" || true
	@echo "Local processes stopped"

# Stop and remove containers
down:
	docker compose down
	@echo "Docker containers stopped"

# Restart containers
restart: down docker

# Show logs
logs:
	docker compose logs -f

# Open a shell in the backend container
shell:
	docker compose exec backend /bin/bash

# Run system tests
test:
	@echo "Running system tests..."
	@if [ -f .venv/bin/python ]; then \
		.venv/bin/python quick_start.py; \
	else \
		echo "Please run 'make setup-local' first for testing"; \
	fi

# Run interactive demo  
demo:
	@echo "Starting interactive demo..."
	@if [ -f .venv/bin/python ]; then \
		.venv/bin/python -c "exec(open('quick_start.py').read())"; \
	else \
		echo "Please run 'make setup-local' first for demo"; \
	fi

# Check system health
health:
	@echo "Checking system health..."
	curl -s http://localhost:8000/health || echo "Backend not responding"

# Clean up containers, images, and cache files
clean:
	@echo "Cleaning up..."
	docker compose down --rmi all --volumes --remove-orphans || true
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Cleanup completed"

# Deep clean including virtual environment
deep-clean: clean
	rm -rf .venv
	docker system prune -af
	@echo "Deep cleanup completed"

# Show container status
status:
	docker compose ps

# Help message
help:
	@echo "🚀 ERP System - Available Commands"
	@echo ""
	@echo "=== RECOMMENDED (Docker - Zero Setup) ==="
	@echo "  make docker      - Build and start with Docker (default)"
	@echo "  make down        - Stop Docker containers"
	@echo "  make restart     - Restart Docker containers"
	@echo "  make logs        - Show Docker logs"
	@echo ""
	@echo "=== LOCAL DEVELOPMENT ==="
	@echo "  make setup-local - Install dependencies locally (first time)"
	@echo "  make start-local - Start locally (no Docker)"
	@echo "  make stop-local  - Stop local processes"
	@echo "  make test        - Run system tests (requires setup-local)"
	@echo "  make demo        - Run interactive demo (requires setup-local)"
	@echo ""
	@echo "=== MAINTENANCE ==="
	@echo "  make build       - Build Docker containers only"
	@echo "  make shell       - Open shell in backend container"
	@echo "  make health      - Check system health"
	@echo "  make status      - Show container status"
	@echo "  make clean       - Clean containers and cache files"
	@echo "  make deep-clean  - Clean everything including venv"
	@echo ""
	@echo "💡 Quick Start: Just run 'make docker' - it handles everything!"
