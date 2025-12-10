# Alembic Migrations

This directory contains Alembic database migration scripts.

## Current Migrations

- **001_initial_schema.py**: Initial database schema with user, movie, and user_movies tables

## Running Migrations

Migrations run automatically when the Docker container starts. To run manually:

### In Docker
```bash
# Upgrade to latest
docker-compose exec web alembic upgrade head

# Create new migration
docker-compose exec web alembic revision --autogenerate -m "description"

# View current revision
docker-compose exec web alembic current

# View history
docker-compose exec web alembic history
```

### Locally (if not using Docker)
```bash
# Set DATABASE_URL environment variable first
export DATABASE_URL=postgresql://user:pass@localhost/dbname

# Then run migrations
alembic upgrade head
```

## Creating New Migrations

1. Modify models in `datamanager/data_models.py`
2. Generate migration: `docker-compose exec web alembic revision --autogenerate -m "your description"`
3. Review the generated migration in `alembic/versions/`
4. Test: `docker-compose exec web alembic upgrade head`

