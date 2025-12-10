# Bellweaver - Quick Start Guide

Get up and running in 5 minutes.

## Choose Your Setup Method

### Option 1: Docker (Recommended - Easiest)

See **[Docker Deployment Guide](docker-deployment.md)** for complete instructions.

Quick start:
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your Compass credentials
# Then build and start
docker-compose up -d

# Sync data
docker exec -it bellweaver bellweaver compass sync

# Access at http://localhost:5000
```

### Option 2: Local Development Setup

## Prerequisites

- Python 3.10+ (currently using 3.12.9)
- Poetry for dependency management
- Node.js 20+ (for frontend development)
- [Task](https://taskfile.dev) - Task runner (optional but recommended)

## First Time Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/jkairys/bellweaver.git
    cd bellweaver
    ```

2.  **Copy environment template**: From the project root, copy the `.env.example` file to `.env`.
    ```bash
    cp .env.example .env
    ```

3.  **Configure `.env`**: Edit your `.env` file to set `COMPASS_MODE` and, if using real mode, your Compass credentials.
    ```dotenv
    # Use mock mode for local development
    COMPASS_MODE=mock

    # Configure real Compass credentials if needed (only when COMPASS_MODE=real)
    COMPASS_BASE_URL=https://your-school.compass.education
    COMPASS_USERNAME=your_username
    COMPASS_PASSWORD=your_password

    # Claude API Key (required for filtering)
    CLAUDE_API_KEY=your-anthropic-api-key
    ```
    **Note**: In mock mode, the credential values don't matter (they're not used), but they are required by the client interface.

4.  **Install all dependencies**:

    **Option A: Using Task (Recommended)**
    ```bash
    task setup
    ```

    **Option B: Manual Installation**
    ```bash
    # Install compass-client package first
    cd packages/compass-client
    poetry install --with dev

    # Install bellweaver package (includes compass-client as a path dependency)
    cd ../bellweaver
    poetry install --with dev

    # Install frontend dependencies
    cd ../../frontend
    npm install
    ```


## Using the CLI

Run CLI commands from the `packages/bellweaver/` directory:

```bash
cd packages/bellweaver

# Sync data from Compass (runs in mock mode by default if configured)
poetry run bellweaver compass sync

# Manage mock data (validate, update from real API)
poetry run bellweaver mock --help

# Start the API server
poetry run bellweaver api serve
```

## Running the Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Start development server
npm run dev

# Access at http://localhost:3000
# API calls are proxied to backend at http://localhost:5000
```

## Running Tests

### Using Task (Recommended)

From the project root:

```bash
task test              # Run all tests across all packages
task test:unit         # Run unit tests only (excludes integration tests)
```

### Manual Testing

Navigate to the respective package directory to run tests:

```bash
# Test bellweaver package (uses mock compass-client by default)
cd packages/bellweaver && poetry run pytest -v

# Test compass-client package (unit tests only)
cd packages/compass-client && poetry run pytest -v -m "not integration"

# Run integration tests (requires real API access)
cd packages/compass-client && poetry run pytest -v -m "integration"
```

## Development Commands

### Using Task (Recommended)

From the project root:

```bash
# Development workflow
task dev                    # Start both frontend and backend dev servers
task format                 # Run formatters with auto-fix (ruff --fix, black)
task lint                   # Run all linters (ruff, flake8, mypy)
task test                   # Run all tests
task clean                  # Clean build artifacts and caches

# Package-specific commands
task backend:format         # Format both backend packages
task backend:lint           # Lint both backend packages
task frontend:dev           # Start only frontend dev server
task backend:serve          # Start only backend API server
```

### Manual Commands

Run development commands from the respective package directory:

#### Python Packages (from `packages/bellweaver/` or `packages/compass-client/`)

```bash
# Format code
poetry run ruff check --fix .       # Auto-fix with ruff
poetry run black .                  # Format with black

# Lint code
poetry run ruff check .             # Check with ruff
poetry run flake8 .                 # Check with flake8
poetry run mypy .                   # Type check with mypy

# Install new packages
poetry add package-name                # Production
poetry add --group dev package-name    # Development only
```

#### Frontend (from `frontend/`)

```bash
# Start dev server
npm run dev

# Build for production
npm run build
```

## Project Structure

This project is a **monorepo** containing two independent Python packages (`compass-client`, `bellweaver`) and a Frontend application (`frontend`).

```
bellweaver/
├── packages/                      # Python packages (monorepo root for Python code)
│   ├── compass-client/            # Independent Compass API client library
│   │   ├── compass_client/        # Source code for the compass-client package
│   │   ├── data/mock/             # Mock data files
│   │   ├── tests/                 # Unit and integration tests for compass-client
│   │   └── pyproject.toml         # Poetry configuration for compass-client
│   │
│   └── bellweaver/                # Main Bellweaver application
│       ├── bellweaver/            # Source code for the bellweaver package
│       │   ├── cli/               # CLI interface
│       │   ├── api/               # Flask REST API
│       │   ├── filtering/         # LLM filtering logic
│       │   ├── db/                # Database layer
│       │   ├── mappers/           # Domain mappers
│       │   ├── models/            # Data models
│       │   └── services/          # Application services
│       ├── tests/                 # Unit and integration tests for bellweaver
│       └── pyproject.toml         # Poetry configuration for bellweaver (depends on compass-client)
│
├── frontend/                      # React frontend application
├── docs/                          # Project documentation
├── .github/workflows/             # GitHub Actions CI/CD workflows
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules
├── docker-compose.yml             # Docker Compose configuration
├── Dockerfile                     # Docker build configuration
└── README.md                      # Main project README
```

## Troubleshooting

-   **"Module 'compass_client' not found"**: Ensure `compass-client` is installed in your environment by running `cd packages/compass-client && poetry install`. Then, from `packages/bellweaver`, run `poetry install`.
-   **"Authentication failed" in real mode**: Verify your Compass credentials and `COMPASS_BASE_URL` in your `.env` file.
-   **Invalid mock data**: Run `cd packages/compass-client && poetry run python -m compass_client.cli mock validate` to check mock data integrity.
-   **Poetry/Virtual environment issues?**:
    ```bash
    # From the respective package directory (e.g., packages/bellweaver)
    poetry lock --refresh
    poetry env remove python # Removes existing virtual environment
    poetry install --with dev
    ```

## Next Steps

See **[docs/index.md](docs/index.md)** for complete project documentation and the development roadmap.
