# Miradi Copilot

A Python-based application using FastAPI and Neo4j for graph-based data processing and API services.

## Project Structure

```
miradi-copilot/
├── api/           # FastAPI application and routes
├── etl/           # Extract, Transform, Load processes
├── graph/         # Neo4j graph database operations
├── tests/         # Unit and integration tests
├── data/          # Data files and datasets
├── docs/          # Documentation
├── .vscode/       # VS Code configuration
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

- Python 3.11+
- Neo4j database
- Virtual environment (recommended)

## Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git

### 1. Start Neo4j Database
Start the Neo4j database using Docker Compose:
```bash
docker-compose up -d neo4j
```

This will:
- Start Neo4j 5.15 Community Edition
- Expose Neo4j Browser on http://localhost:7474
- Expose Bolt protocol on bolt://localhost:7687
- Use credentials: `neo4j/password123`
- Create persistent volumes for data storage

To stop Neo4j:
```bash
docker-compose down
```

To view Neo4j logs:
```bash
docker-compose logs neo4j
```

### 2. Python Environment Setup

**Create and activate virtual environment:**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the example environment file and customize as needed:
```bash
cp .env.example .env
```

The default configuration works with the Docker Neo4j setup:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
NEO4J_DATABASE=neo4j
API_HOST=0.0.0.0
API_PORT=8000
```

## Development

### Quick Setup with Makefile
The project includes a Makefile for common development tasks:

```bash
# Complete development setup
make dev-setup

# Or step by step:
make venv                # Create virtual environment
make install-dev         # Install all dependencies + dev tools
make docker-up           # Start Neo4j database
```

### Available Make Commands
```bash
make help               # Show all available commands
make venv               # Create virtual environment
make install            # Install production dependencies
make install-dev        # Install development dependencies
make test               # Run tests
make test-coverage      # Run tests with coverage report
make format             # Format code with black and isort
make lint               # Run linting (flake8, mypy, pylint)
make clean              # Clean up cache files
make run-api            # Start FastAPI development server
make docker-up          # Start Neo4j with Docker
make docker-down        # Stop Docker services
make check              # Run format, lint, and test (pre-commit check)
```

### Manual Commands

**Running the API:**
```bash
make run-api
# or manually:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Running Tests:**
```bash
make test
# or with coverage:
make test-coverage
# or manually:
pytest tests/ -v
```

**Code Formatting:**
```bash
make format
# or manually:
black .
isort .
```

**Linting:**
```bash
make lint
# or manually:
flake8 api etl graph tests
mypy api etl graph
pylint api etl graph
```

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks (included in make install-dev)
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

Pre-commit will automatically run:
- Code formatting (black, isort)
- Linting (flake8, mypy)
- Security checks (bandit)
- Basic file checks (trailing whitespace, etc.)

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Neo4j**: Graph database for complex relationship modeling
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for FastAPI applications
- **Pytest**: Testing framework

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### 📋 **Core Documentation**
- **[Architecture Overview](docs/01-architecture-overview.md)**: System design and component architecture
- **[Domain Model](docs/02-domain-model.md)**: Conservation concepts and Miradi terminology
- **[Graph Schema](docs/04-graph-schema.md)**: Neo4j database design and query patterns

### 🔧 **Development Guides**
- **[Development Guide](docs/07-development-guide.md)**: Best practices for Cline-assisted development
- **[Data Flow](docs/03-data-flow.md)**: ETL pipeline and data processing *(template)*
- **[GraphRAG Architecture](docs/06-rag-architecture.md)**: AI query processing *(template)*

### 🚀 **Operations**
- **[Deployment Guide](docs/08-deployment.md)**: Production deployment procedures *(template)*
- **[Schema Documentation](docs/schemas/)**: Miradi file format analysis

### 📊 **Visual Resources**
- **[Diagrams](docs/diagrams/)**: System diagrams and visualization standards

For a complete overview, see the [Documentation Index](docs/README.md).

## Contributing

1. Follow PEP 8 style guidelines
2. Write tests for new functionality
3. Update documentation as needed
4. Use type hints throughout the codebase
5. Review the [Development Guide](docs/07-development-guide.md) for AI-assisted development best practices

## License

[Add your license information here]
