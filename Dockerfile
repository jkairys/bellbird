# Multi-stage Dockerfile for Bellweaver
# Builds frontend and backend in a single container

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Build backend and combine
FROM python:3.11-slim AS backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Copy backend dependency files and README
COPY backend/pyproject.toml backend/poetry.lock backend/README.md ./

# Copy backend source code (needed for poetry install to work with scripts)
COPY backend/bellweaver ./bellweaver

# Configure Poetry to not create virtual environment (we're in a container)
RUN poetry config virtualenvs.create false

# Install dependencies AND the package itself (for CLI scripts)
RUN poetry install --only main --no-interaction --no-ansi

# Copy built frontend from frontend-builder stage into backend/bellweaver/static
COPY --from=frontend-builder /app/frontend/dist ./bellweaver/static

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=bellweaver.api
ENV DATABASE_PATH=/app/data/bellweaver.db

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/user', timeout=5)" || exit 1

# Run the application
CMD ["python", "-m", "bellweaver.api"]
