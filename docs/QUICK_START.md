# Bellweaver - Quick Start Guide

Get up and running in 5 minutes.

## Prerequisites

- Python 3.10+ (currently using 3.12.9)
- Poetry for dependency management
- Node.js (for Puppeteer-based Compass authentication)

## First Time Setup

```bash
# 1. Navigate to project
cd /Users/jethro/github/jkairys/bellweaver

# 2. Copy environment template
cp .env.example .env

# 3. Edit with your API keys
# Add your CLAUDE_API_KEY to .env
vim .env

# 4. Verify Poetry is working
poetry --version
poetry env info
```

## Development Commands

```bash
# Run tests
poetry run pytest

# Format code (Black)
poetry run black src tests

# Lint code (Flake8)
poetry run flake8 src tests

# Type check (mypy)
poetry run mypy src

# Install new packages
poetry add package-name

# Run CLI (when implemented)
poetry run bellweaver --help

# Run Flask server (when implemented)
poetry run flask run
```

## Project Structure at a Glance

```
bellweaver/
├── src/                    # Main source code
│   ├── adapters/          # Compass API client (to implement)
│   ├── db/                # Database layer (to implement)
│   ├── filtering/         # Claude API filtering (to implement)
│   ├── models/            # Data models (to implement)
│   ├── api/               # Flask REST API (to implement)
│   ├── cli.py             # CLI entry point (to implement)
│   └── app.py             # Flask app (to implement)
│
├── frontend/              # Web UI (to implement)
├── tests/                 # Unit tests
├── data/                  # Runtime data (SQLite database will go here)
│
├── pyproject.toml         # Poetry configuration
├── .env.example           # Environment template
├── .gitignore             # Git rules
├── README.md              # Full documentation
└── QUICK_START.md         # This file
```

## Current Status

✅ **Authentication Working** - Puppeteer-based Compass client functional
✅ **Tests Passing** - Integration tests with real credentials
⚠️ **Performance Issue** - Logs in on every request (~10-15s)

## Next Steps

See **NEXT_STEPS.md** for current development priorities.

Top priority: Optimize CompassClient session management to avoid repetitive logins.

## Key Documentation

- **INDEX.md** - Documentation navigation
- **NEXT_STEPS.md** - Current development roadmap
- **IMPLEMENTATION_SUMMARY.md** - What's working now
- **MVP_ARCHITECTURE.md** - System design
- **COMPASS_AUTHENTICATION_STRATEGIES.md** - How Compass auth works

## Common Tasks

### Add a new dependency
```bash
poetry add package-name          # Production
poetry add --group dev package   # Development only
```

### Update dependencies
```bash
poetry update
```

### Clean virtual environment
```bash
poetry env remove bellweaver
poetry install --with dev
```

### Export requirements.txt (if needed)
```bash
poetry export -f requirements.txt --output requirements.txt
```

## Environment Variables Explained

```bash
# Your Anthropic API key for Claude access
CLAUDE_API_KEY=sk-ant-xxxxx

# Auto-generated encryption key for credential storage
# Leave empty on first run - it will be generated and saved
BELLWEAVER_ENCRYPTION_KEY=

# Flask settings (optional)
FLASK_ENV=development
FLASK_DEBUG=1

# Database location (optional, defaults to ./data/bellweaver.db)
DATABASE_URL=sqlite:///./data/bellweaver.db
```

## Troubleshooting

**Poetry not finding packages?**
```bash
poetry lock --refresh
poetry install --with dev
```

**Virtual environment issues?**
```bash
poetry env remove bellweaver
poetry install --with dev
```

**Wrong Python version?**
```bash
poetry env info  # Check current Python
pyenv versions   # Check available versions
pyenv global 3.12.9  # Switch version if needed
```

## Next Steps

1. Review **PLAN.md** to understand the project scope
2. Read **MVP_ARCHITECTURE.md** for system design
3. Start implementing **src/db/database.py** - the foundation layer
4. Create **src/db/models.py** with SQLAlchemy ORM models
5. Build mock data in **src/adapters/compass_mock.py**

---

Happy coding! The project is ready to go. 🚀
