# Claude Code Context Guide for Bellweaver

This file documents key information about the Bellweaver project to help Claude Code understand the codebase, architecture, and development context.

## Project Overview

**Bellweaver** is a school calendar event aggregation and filtering tool that consolidates events from multiple sources (Compass, Class Dojo, HubHello, Xplore) and intelligently filters them based on relevance to specific children.

**Problem**: Parents receive overwhelming communication from multiple school sources with no unified view.

**Solution**: Single dashboard showing relevant calendar events for each child, powered by Claude API for intelligent filtering.

## Workflow

- When starting a new context / session, create a new branch on which to commit all changes
  - always start branches by pullling the latest from `main`
  - to determine branch name:
    - summarise the intent of the session into a git-friendly slug, e.g. `add-tabs-to-school-details` and
    - generate a string represntation of the current date in `YYYYMMDD-HH24MISS` format, e.g. `20251201-093322`
  - create a new branch using `<slug>-<date>` e.g. `add-tabs-to-school-details-20241201093322`
  - make changes to files interactively during the session
  - commit changes to the branch as you go - whenever you prompt for input, you should commit your changes before showing the prompt
- When you are done
  - run tests and fix if failing
  - update documentation
  - push the branch to the remote
  - create a pull request using the `gh` cli and let me review and merge it

## When waiting for input, or the task is complete

Use the command line below to notify the user every signle time Claude Code execution finishes, whether it's waiting for input or a task is complete.

```zsh
osascript -e 'display notification "Waiting for your input" with title "Claude Code" sound name "Glass"'
```

## Tech Stack

### Backend

- **Language**: Python
- **Package Manager**: Poetry
- **Web Framework**: Flask
- **Database**: SQLite with SQLAlchemy ORM
- **CLI**: Typer

### Frontend

- **Framework**: React 18
- **Build Tool**: Vite
- **Package Manager**: npm

### Deployment

- **Containerization**: Docker (multi-stage build)
- **Orchestration**: Docker Compose

### Development Tools

- **Task Runner**: Task (Taskfile.yml)
- **Testing**: pytest + pytest-cov
- **Formatting**: black, ruff
- **Linting**: ruff, flake8
- **Type Checking**: mypy

## Environment & Configuration

### Environment Files

The project uses a single `.env` file in the repository root for both Docker and local development:

- **Location**: `.env` (in project root)
- **Template**: `.env.example` (in project root)
- **Usage**:
  - Docker Compose reads this file via `env_file: .env`
  - Local development can read from the same file
- **Setup**: Copy `.env.example` to `.env` and fill in your values

**Note:** The Docker setup mounts `backend/data/` as a volume, so the SQLite database is shared between Docker and local environments. You can use the same database whether running in Docker or locally.

### Required Environment Variables

```bash
# Compass API Mode (mock or real). Defaults to 'real' if not set.
COMPASS_MODE=mock

# Compass API credentials (required only when COMPASS_MODE=real)
COMPASS_USERNAME=your_compass_username
COMPASS_PASSWORD=your_compass_password
COMPASS_BASE_URL=https://your-school.compass.education

# Claude API Key (required for LLM filtering features)
CLAUDE_API_KEY=your-anthropic-api-key-here

# Database Encryption Key (auto-generated on first run if not provided)
BELLWEAVER_ENCRYPTION_KEY=will-be-auto-generated-on-first-run

# Flask Configuration (optional)
FLASK_ENV=development
FLASK_DEBUG=1

# Database location (optional, defaults to packages/bellweaver/data/bellweaver.db)
DATABASE_URL=sqlite:///./packages/bellweaver/data/bellweaver.db
```

See `.env.example` in the project root for the full template.

### Poetry Commands

All Poetry commands should be run from the `packages/bellweaver/` directory or `packages/compass-client/` directory, depending on the context:

```bash
# General commands (run from respective package directory)
cd packages/bellweaver && poetry install --with dev       # Install all bellweaver dependencies
cd packages/compass-client && poetry install --with dev   # Install all compass-client dependencies
cd packages/bellweaver && poetry run pytest               # Run bellweaver tests
cd packages/compass-client && poetry run pytest           # Run compass-client tests
cd packages/bellweaver && poetry add package-name         # Add bellweaver production dependency
cd packages/bellweaver && poetry add --group dev pkg      # Add bellweaver dev dependency

# Bellweaver-specific commands (run from packages/bellweaver/)
cd packages/bellweaver && poetry run bellweaver compass sync  # Sync data from Compass
cd packages/bellweaver && poetry run bellweaver api serve     # Start API server

# compass-client specific commands (run from packages/compass-client/)
cd packages/compass-client && poetry run python -m compass_client.cli refresh-mock-data # Refresh mock data
cd packages/compass-client && poetry run python -m compass_client.cli mock validate     # Validate mock data
```

### Task Runner Commands

The project uses [Task](https://taskfile.dev) (a Make alternative) to standardize development workflows. All task commands should be run from the project root:

```bash
# First time setup - installs all dependencies
task setup

# Development workflow
task dev                    # Start both frontend and backend dev servers concurrently
task test                   # Run all tests across all packages
task test:unit              # Run unit tests only (excludes integration tests)
task lint                   # Run all linters (ruff, flake8, mypy)
task format                 # Run formatters with auto-fix (ruff --fix, black)
task clean                  # Clean all build artifacts and caches

# Frontend-specific tasks
task frontend:install       # npm install
task frontend:dev           # Start Vite dev server
task frontend:build         # Production build

# Backend-specific tasks
task backend:install        # Install both packages with Poetry
task backend:test           # Run tests for both packages
task backend:lint           # Lint both packages
task backend:format         # Format both packages
task backend:serve          # Start Flask API server

# Individual package tasks
task backend:bellweaver:test
task backend:bellweaver:lint
task backend:bellweaver:format
task backend:compass-client:test
task backend:compass-client:test:integration
task backend:compass-client:refresh-mock
```

### Docker Commands

All Docker commands should be run from the project root:

```bash
docker-compose build            # Build the container
docker-compose up -d            # Start in detached mode
docker-compose logs -f          # View logs
docker-compose down             # Stop and remove container

# Execute commands inside the container
docker exec -it bellweaver bellweaver compass sync
docker exec -it bellweaver bash
```

### Files to Never Commit

- `.env` (contains API keys and credentials)
- `packages/*/venv/` (Python virtual environments)
- `packages/*/.venv/` (Poetry virtual environments)
- `packages/*/data/*.db` (user data - SQLite database)
- `frontend/node_modules/` (npm dependencies)
- `frontend/dist/` (built frontend files)
- `__pycache__/` and `.pytest_cache/`

### Commit Message Style

- Clear, imperative ("Add database models" not "Added")
- Reference the component ("db:" or "api:" prefix)
- Example: "db: add encrypted credential storage"

## Documentation

For detailed information, see:

- **[docs/index.md](docs/index.md)** - Complete documentation index, current status, and roadmap
- **[docs/quick-start.md](docs/quick-start.md)** - Setup instructions
- **[docs/architecture.md](docs/architecture.md)** - System design and technical decisions

## References & Resources

- [Unofficial Compass API Client](https://github.com/heheleo/compass-education)
- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Poetry Documentation](https://python-poetry.org/docs)

## Active Technologies

- Python 3.11+ (Poetry-managed)
- Flask (Web Framework), SQLAlchemy 2.0 (ORM), Typer (CLI)
- Pydantic (Data Validation), Requests, BeautifulSoup4
- React 18 (Frontend), Vite (Build Tool)
- SQLite (local database), JSON files for mock data
- Docker (Containerization), Docker Compose (Orchestration)
- GitHub Actions (CI/CD)

## Recent Changes

- **002-compass-api-decoupling**: Refactored Compass API integration into a new `compass-client` package, introduced multi-package monorepo structure, mock data infrastructure, and updated CI/CD workflows.
- **001-family-management**: Implemented initial family management features, including Python 3.10+ stack with Flask, SQLAlchemy, Typer, Pydantic, React 18, and Vite.
