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

- **Testing**: pytest + pytest-cov
- **Formatting**: black
- **Linting**: flake8
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
# Compass API credentials (required)
COMPASS_USERNAME=your_compass_username
COMPASS_PASSWORD=your_compass_password
COMPASS_BASE_URL=https://your-school.compass.education

# Claude API Key (required)
CLAUDE_API_KEY=your-anthropic-api-key-here

# Database Encryption Key (auto-generated on first run if not provided)
BELLWEAVER_ENCRYPTION_KEY=will-be-auto-generated-on-first-run

# Flask Configuration (optional)
FLASK_ENV=development
FLASK_DEBUG=1

# Database location (optional, defaults to data/bellweaver.db)
DATABASE_URL=sqlite:///./data/bellweaver.db
```

See `.env.example` in the project root for the full template.

### Poetry Commands

All Poetry commands should be run from the `packages/compass-client` directory or `packages/bellweaver` directory:

```bash
poetry install --with dev       # Install all dependencies
poetry run pytest               # Run tests
poetry add package-name         # Add production dependency
poetry add --group dev pkg      # Add dev dependency
poetry run bellweaver compass sync  # Sync data from Compass
poetry run bellweaver api serve     # Start API server
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
- `.venv/` (virtual environment)
- `bellweaver.db` (user data)
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

- Python 3.10+ + Flask (web framework), SQLAlchemy 2.0 (ORM), Typer (CLI), Pydantic (validation), React 18 (frontend), Vite (build tool) (001-family-management)
- SQLite with SQLAlchemy ORM (local-first, PostgreSQL-ready patterns) (001-family-management)
- Python 3.11 (Poetry-managed) (002-compass-api-decoupling)
- SQLite with SQLAlchemy ORM (Bellweaver), JSON files for mock data (Compass package) (002-compass-api-decoupling)

## Recent Changes

- 001-family-management: Added Python 3.10+ + Flask (web framework), SQLAlchemy 2.0 (ORM), Typer (CLI), Pydantic (validation), React 18 (frontend), Vite (build tool)
