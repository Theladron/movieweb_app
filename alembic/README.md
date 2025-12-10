# Alembic Migrations

This directory contains Alembic database migration scripts.

## Current Migrations

- **001_initial_schema.py**: Initial database schema with user, movie, and user_movies tables

## Running Migrations (SQLite-first)

Default database: `sqlite:///data/movies.db`.

```bash
mkdir -p data
export DATABASE_URL=sqlite:///data/movies.db
alembic upgrade head
```

## Creating New Migrations

1. Modify models in `datamanager/data_models.py`
2. Generate migration: `alembic revision --autogenerate -m "your description"`
3. Review the generated migration in `alembic/versions/`
4. Test: `alembic upgrade head`

