.PHONY: help venv install install-dev test format lint clean run-api docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  venv         Create virtual environment"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  format       Format code with black and isort"
	@echo "  lint         Run linting with flake8 and mypy"
	@echo "  clean        Clean up cache files and build artifacts"
	@echo "  run-api      Start the FastAPI development server"
	@echo "  docker-up    Start Neo4j with Docker Compose"
	@echo "  docker-down  Stop Docker services"

# Virtual environment setup
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  macOS/Linux: source venv/bin/activate"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v --tb=short

test-coverage:
	pytest tests/ --cov=api --cov=etl --cov=graph --cov-report=html --cov-report=term

# Code formatting and linting
format:
	black .
	isort .

lint:
	flake8 api etl graph tests
	mypy api etl graph
	pylint api etl graph

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/

# Development server
run-api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Docker commands
docker-up:
	docker-compose up -d neo4j

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs neo4j

# Development workflow
dev-setup: venv install-dev
	@echo "Development environment setup complete!"
	@echo "Don't forget to activate your virtual environment:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  macOS/Linux: source venv/bin/activate"

# Check everything before commit
check: format lint test
	@echo "All checks passed! Ready to commit."
