.PHONY: help setup build up down restart logs shell clean status test demo health all start stop deep-clean

# Default target when running make
all: setup up

# Setup environment and dependencies
setup:
	@echo "Setting up ERP system..."
	@echo "Creating virtual environment..."
	python3 -m venv .venv || true
	@echo "Installing dependencies..."
	.venv/bin/pip install -r requirements.txt
	@echo "Creating sample database..."
	.venv/bin/python create_sample_db.py
	@echo "Setup completed successfully"

# Build the Docker containers
build:
	docker compose build

# Start the system (Docker)
up: 
	docker compose up -d
	@echo "ERP system started!"
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend UI: http://localhost:8501"

# Start locally (without Docker)
start:
	@echo "Starting ERP system locally..."
	cd backend && ../.venv/bin/python api.py &
	sleep 3
	cd frontend && ../.venv/bin/python -m streamlit run streamlit_app.py --server.port=8501 &
	@echo "ERP system started locally!"

# Stop and remove containers
down:
	docker compose down
	@echo "ERP system stopped"

# Stop local processes
stop:
	pkill -f "python.*api.py" || true
	pkill -f "streamlit run" || true
	@echo "Local processes stopped"

# Restart containers
restart: down up

# Show logs
logs:
	docker compose logs -f

# Open a shell in the backend container
shell:
	docker compose exec backend /bin/bash

# Run system tests
test:
	@echo "Running system tests..."
	.venv/bin/python quick_start.py

# Run interactive demo
demo:
	@echo "Starting interactive demo..."
	.venv/bin/python -c "exec(open('quick_start.py').read())"

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
	@echo "Available commands:"
	@echo "  make setup       - Install dependencies and create sample database"
	@echo "  make build       - Build Docker containers"
	@echo "  make up          - Start containers (recommended)"
	@echo "  make start       - Start locally without Docker"
	@echo "  make down        - Stop containers"
	@echo "  make stop        - Stop local processes"
	@echo "  make restart     - Restart containers"
	@echo "  make logs        - Show container logs"
	@echo "  make shell       - Open shell in backend container"
	@echo "  make test        - Run system tests"
	@echo "  make demo        - Run interactive demo"
	@echo "  make health      - Check system health"
	@echo "  make clean       - Clean containers and cache files"
	@echo "  make deep-clean  - Clean everything including venv"
	@echo "  make status      - Show container status"
