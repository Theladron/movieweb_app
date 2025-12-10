# Docker Setup for Movie Web App

This document explains how to run the Movie Web App using Docker with PostgreSQL.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

1. **Create a `.env` file** in the root directory:
   ```bash
   cp .env.example .env
   ```
   
   Or create it manually with:
   ```env
   # Flask Configuration
   FLASK_ENV=development
   FLASK_PORT=5000

   # PostgreSQL Database Configuration
   POSTGRES_USER=movieuser
   POSTGRES_PASSWORD=moviepass
   POSTGRES_DB=moviesdb
   POSTGRES_PORT=5432

   # OMDb API Key (required for fetching movie data)
   OMDB_API_KEY=your_omdb_api_key_here
   ```

2. **Build and start the containers**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Web app: http://localhost:5000
   - PostgreSQL: localhost:5432 (credentials from .env file)

## How It Works

### Services

- **web**: Flask application container
  - Runs Alembic migrations on startup
  - Serves the Flask app on port 5000
  - Connects to PostgreSQL database

- **db**: PostgreSQL 15 database container
  - Data persisted in Docker volume `postgres_data`
  - Health checks ensure database is ready before web app starts

### Database Migrations

Alembic automatically runs migrations when the web container starts. The initial migration (`001_initial_schema.py`) creates all necessary tables:
- `user`
- `movie`
- `user_movies`

### Volume Persistence

- `postgres_data`: PostgreSQL database data (persists between restarts)
- `static_volume`: Static files volume

## Common Commands

### Start services
```bash
docker-compose up
```

### Start in detached mode
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes database data)
```bash
docker-compose down -v
```

### View logs
```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Access PostgreSQL shell
```bash
docker-compose exec db psql -U movieuser -d moviesdb
```

### Access Flask container shell
```bash
docker-compose exec web bash
```

### Run Alembic commands
```bash
# Create a new migration
docker-compose exec web alembic revision --autogenerate -m "description"

# Upgrade database
docker-compose exec web alembic upgrade head

# Downgrade database
docker-compose exec web alembic downgrade -1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_PORT` | Flask port | `5000` |
| `POSTGRES_USER` | PostgreSQL username | `movieuser` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `moviepass` |
| `POSTGRES_DB` | Database name | `moviesdb` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `OMDB_API_KEY` | OMDb API key (required) | - |

## Troubleshooting

### Database connection errors
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check logs: `docker-compose logs db`
- Verify environment variables in `.env` file

### Migration errors
- Check if migrations are up to date: `docker-compose exec web alembic current`
- View migration history: `docker-compose exec web alembic history`
- Reset database (⚠️ data loss): `docker-compose down -v && docker-compose up`

### Port conflicts
- Change ports in `.env` file if 5000 or 5432 are already in use

## Development

The application code is mounted as a volume, so code changes will be reflected immediately (after Flask auto-reload). However, you may need to restart containers for dependency changes.

To rebuild after dependency changes:
```bash
docker-compose up --build
```

## Production Considerations

For production deployment, consider:
- Using strong passwords in `.env`
- Setting `FLASK_ENV=production`
- Using a reverse proxy (nginx)
- Setting up SSL/TLS
- Database backups
- Environment variable management (secrets manager)

