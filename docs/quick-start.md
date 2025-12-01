# Bellweaver - Quick Start Guide

Get up and running in 5 minutes.

## Choose Your Setup Method

### Option 1: Docker (Recommended - Easiest)

See **[Docker Deployment Guide](docker-deployment.md)** for complete instructions.

Quick start:
```bash
# Copy environment file
cp .env.docker.example .env.docker

# Edit .env.docker with your Compass credentials
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

## First Time Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Copy environment template
cp .env.example .env

# 3. Edit with your credentials
vim .env

# Add the following to .env:
# COMPASS_USERNAME=your_compass_username
# COMPASS_PASSWORD=your_compass_password
# COMPASS_BASE_URL=https://your-school.compass.education
# CLAUDE_API_KEY=sk-ant-xxxxx (optional, for future filtering features)

# 4. Install dependencies
poetry install --with dev
```

## Using the CLI

```bash
cd backend

# Sync data from Compass
poetry run bellweaver compass sync

# Sync with custom date range
poetry run bellweaver compass sync --days 30

# Start the API server
poetry run bellweaver api serve

# Start with debug mode
poetry run bellweaver api serve --debug
```

## Running the Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# Access at http://localhost:3000
# API calls are proxied to backend at http://localhost:5000
```

## Running Tests

```bash
cd backend

# Run all tests
poetry run pytest -v

# Run integration tests with real Compass credentials
poetry run pytest tests/test_compass_client_real.py -v

# Run specific test
poetry run pytest tests/test_compass_client_real.py::test_login -v
```

## Development Commands

```bash
cd backend

# Format code (Black)
poetry run black src tests

# Lint code (Flake8)
poetry run flake8 src tests

# Type check (mypy)
poetry run mypy src

# Install new packages
poetry add package-name                # Production
poetry add --group dev package-name    # Development only
```

## Project Structure

```
bellweaver/
├── backend/
│   ├── bellweaver/
│   │   ├── adapters/
│   │   │   ├── compass.py         # ✅ HTTP-based Compass client (working)
│   │   │   └── compass_mock.py    # ✅ Mock client for testing (working)
│   │   ├── filtering/
│   │   │   └── llm_filter.py      # ✅ Claude API filtering (implemented, not integrated)
│   │   ├── db/
│   │   │   └── credentials.py     # ✅ Credential encryption (implemented, not integrated)
│   │   ├── api/                   # ⏳ TODO - Flask API routes
│   │   └── models/                # ⏳ TODO - Data models
│   ├── tests/
│   │   ├── test_compass_client_real.py  # ✅ Integration tests (working)
│   │   └── test_fixtures.py             # ✅ Fixture tests (working)
│   ├── pyproject.toml            # Poetry configuration
│   └── .env.example              # Environment template
│
├── docs/                         # Documentation
└── README.md                     # Project overview
```

## Current Status

✅ **Compass Authentication** - HTTP-based client working (~1 second)
✅ **Calendar Fetching** - Can retrieve events from Compass API
✅ **Mock Data** - Realistic test data available for development
✅ **Tests Passing** - Integration tests with real credentials working
⏳ **In Progress** - Database integration, API routes, filtering pipeline

## Troubleshooting

**Poetry not finding packages?**

```bash
cd backend
poetry lock --refresh
poetry install --with dev
```

**Virtual environment issues?**

```bash
cd backend
poetry env remove python
poetry install --with dev
```

**Tests failing?**

```bash
# Check .env file has correct credentials
cat backend/.env

# Ensure you're in the backend directory
cd backend
poetry run pytest -v
```

## Next Steps

See `docs/index.md` for complete project documentation and development roadmap.
