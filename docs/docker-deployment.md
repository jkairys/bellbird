# Docker Deployment Guide

This guide explains how to deploy Bellweaver using Docker, which packages both the frontend and backend in a single container.

## Architecture

The Docker deployment uses a multi-stage build:

1. **Stage 1 (frontend-builder)**: Builds the React frontend using Node.js and Vite
2. **Stage 2 (backend)**: Installs Python dependencies and copies the built frontend into `bellweaver/static/`

The final container runs a Flask application that:
- Serves the React SPA from `/`
- Serves REST API endpoints from `/api/*`
- Handles client-side routing by serving `index.html` for non-API routes

## Prerequisites

- Docker (and Docker Compose recommended)
- Compass API credentials

## Quick Start with Docker Compose

### 1. Create environment file

Copy the example environment file and fill in your Compass credentials:

```bash
cp .env.docker.example .env.docker
```

Edit `.env.docker` with your credentials:

```bash
COMPASS_USERNAME=your_compass_username
COMPASS_PASSWORD=your_compass_password
COMPASS_BASE_URL=https://your-school.compass.education
```

**Important:** The `.env.docker` file is mounted into the container and shared with your local environment. When running locally (outside Docker), both environments use the same configuration and database.

### 2. Ensure data directory exists

The database directory is automatically created, but you can verify it exists:

```bash
mkdir -p backend/data
```

**Important:** The `backend/data` directory is mounted as a volume in the container, so the SQLite database (`bellweaver.db`) is shared between Docker and local environments. This means:
- Data persists when the container is stopped/restarted
- The same database is used whether running in Docker or locally
- No data migration needed when switching between Docker and local development

### 3. Build and start the application

```bash
# Build the image
docker-compose build

# Start the container in detached mode
docker-compose up -d
```

This will:
- Build the multi-stage Docker image (frontend + backend)
- Start the container in detached mode
- Mount `backend/data` for database persistence
- Mount `.env.docker` for configuration
- Expose the application on port 5000

### 4. Sync data from Compass

Before the dashboard will show data, you need to sync from Compass:

```bash
# Run sync inside the container
docker exec -it bellweaver bellweaver compass sync
```

Alternatively, you can run the sync command locally (outside Docker) and it will use the same database:

```bash
cd backend
poetry run bellweaver compass sync
```

Both approaches write to the same `backend/data/bellweaver.db` file.

### 5. Access the application

Open your browser to:
- **Frontend**: http://localhost:5000
- **API**: http://localhost:5000/api/user or http://localhost:5000/api/events

### 6. View logs

```bash
docker-compose logs -f
```

### 7. Stop the application

```bash
docker-compose down
```

**Note:** This stops and removes the container but preserves the database in `backend/data/`. To also remove the database, manually delete the data directory:

```bash
rm -rf backend/data/
```

## Manual Docker Commands

If you prefer not to use Docker Compose:

### Build the image

```bash
docker build -t bellweaver:latest .
```

### Run the container

```bash
docker run -d \
  --name bellweaver \
  -p 5000:5000 \
  -v $(pwd)/backend/data:/app/data \
  --env-file .env.docker \
  bellweaver:latest
```

**Note:** Using `--env-file .env.docker` loads all environment variables from the file. Alternatively, you can pass them individually with `-e` flags:

```bash
docker run -d \
  --name bellweaver \
  -p 5000:5000 \
  -v $(pwd)/backend/data:/app/data \
  -e COMPASS_USERNAME=your_username \
  -e COMPASS_PASSWORD=your_password \
  -e COMPASS_BASE_URL=https://your-school.compass.education \
  -e DATABASE_PATH=/app/data/bellweaver.db \
  bellweaver:latest
```

### Sync data

```bash
docker exec -it bellweaver bellweaver compass sync
```

### View logs

```bash
docker logs -f bellweaver
```

### Stop and remove the container

```bash
docker stop bellweaver
docker rm bellweaver
```

The database persists in `backend/data/` even after container removal.

## API Routes

All API endpoints are prefixed with `/api`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/user` | GET | Get latest user details from Compass |
| `/api/events` | GET | Get calendar events from Compass |

## Troubleshooting

### Container fails health check

The health check tries to access `/api/user`. If it fails, check:

1. Database has been synced with Compass data:
   ```bash
   docker exec -it bellweaver bellweaver compass sync
   ```

2. Credentials are correct in `.env` file

3. Check logs for errors:
   ```bash
   docker-compose logs
   ```

### Frontend shows blank page

1. Check that the build completed successfully:
   ```bash
   docker logs bellweaver | grep "frontend"
   ```

2. Verify static files exist in the image:
   ```bash
   docker exec -it bellweaver ls -la /app/bellweaver/static
   ```

### API returns 404

Ensure you're using the `/api` prefix for all API calls:
- ✅ Correct: `http://localhost:5000/api/user`
- ❌ Incorrect: `http://localhost:5000/user`

### Database not persisting

Check that the data directory is mounted correctly:

```bash
docker inspect bellweaver | grep -A 10 Mounts
```

You should see `/app/data` mounted to your local `./backend/data` directory.

### Data synced in Docker not visible locally (or vice versa)

Both environments should share the same database. Verify:

1. Check that docker-compose.yml mounts `./backend/data:/app/data`
2. Check that `DATABASE_PATH=/app/data/bellweaver.db` is set
3. Verify the database file exists:
   ```bash
   ls -la backend/data/bellweaver.db
   ```

If you synced data locally, it should be visible in Docker and vice versa.

## Production Considerations

### Security

1. **Never commit `.env` file** - it contains sensitive credentials
2. **Use secrets management** in production (e.g., Docker secrets, Kubernetes secrets)
3. **Enable HTTPS** using a reverse proxy (nginx, Traefik, Caddy)

### Scaling

This is a single-container deployment suitable for personal use. For production:

1. Use a reverse proxy (nginx/Traefie/Caddy) for HTTPS
2. Consider using a managed database instead of SQLite
3. Implement proper backup strategy for the database

### Updating

To update to a new version:

```bash
# Pull latest code
git pull

# Rebuild image
docker-compose build

# Restart container
docker-compose up -d
```

## Development Workflows

### Shared Environment Between Docker and Local

The Docker setup is designed to work seamlessly with local development:

**Shared Resources:**
- **Database**: `backend/data/bellweaver.db` is mounted into the container
- **Environment**: `.env.docker` contains credentials used by both Docker and local development
- **State**: Changes made in Docker are visible locally and vice versa

**Use Cases:**

1. **Run API in Docker, develop locally:**
   ```bash
   # Start API in Docker
   docker-compose up -d

   # Sync data (can run locally or in Docker)
   poetry run bellweaver compass sync

   # Access API at http://localhost:5000
   ```

2. **Run everything in Docker:**
   ```bash
   docker-compose up -d
   docker exec -it bellweaver bellweaver compass sync
   # Access at http://localhost:5000
   ```

3. **Local development mode (separate frontend/backend):**
   ```bash
   # Terminal 1: Backend
   cd backend
   poetry run bellweaver api serve --debug

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   # Access at http://localhost:3000 (proxies to backend on 5000)
   ```

### Development vs Production Modes

**Development (local):**
- Frontend: `npm run dev` on port 3000 with hot reload
- Backend: `poetry run bellweaver api serve --debug` on port 5000
- Vite proxy forwards `/api/*` requests to backend
- Fast iteration with hot module replacement

**Production (Docker):**
- Frontend: Built static files served by Flask from `/`
- Backend: Flask API serves from `/api/*`
- Single container on port 5000
- Client-side routing handled by Flask fallback to `index.html`
- No Vite dev server overhead
