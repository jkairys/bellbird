# Bellweaver Backend

This is the backend application for Bellweaver - a school calendar event aggregation and filtering tool.

## Setup

### Prerequisites
- Python 3.10+
- Poetry (for dependency management)
- Compass account credentials (for real API testing)
- Claude API key (from Anthropic)

### Installation

1. **Install dependencies with Poetry**:
```bash
poetry install --with dev
```

2. **Set up environment variables**:
```bash
cp .env.example .env
```

Then edit `.env` with your actual values:
```bash
CLAUDE_API_KEY=your-anthropic-api-key-here
BELLWEAVER_ENCRYPTION_KEY=  # Will be auto-generated on first run
```

3. **Verify installation**:
```bash
poetry run pytest
```

## Usage

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
poetry run black src tests
poetry run flake8 src tests
poetry run mypy src
```

## Documentation

See the main [README.md](../README.md) in the root directory for complete documentation.
