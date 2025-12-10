# MovieWeb App

A Flask-based web application for managing personal movie collections. Users can create profiles, add movies from the OMDb API, and rate their favorite films.

## Features

- **User Management**: Create and manage user profiles
- **Movie Collection**: Add movies from OMDb API to personal collections
- **Personal Ratings**: Rate movies with your own ratings separate from IMDB ratings
- **RESTful API**: JSON API endpoints for programmatic access
- **Modern UI**: Glassmorphic design with responsive layout

## Project Structure

```
movieweb_app/
├── app.py                 # Flask application factory
├── config.py              # Application configuration (logging, etc.)
├── datamanager/          # Data access layer
│   ├── data_models.py    # SQLAlchemy models
│   └── sqlite_data_manager.py
├── routes/               # Flask route blueprints
│   ├── main.py          # Homepage
│   ├── user.py          # User management
│   ├── movie.py         # Movie management
│   ├── api.py           # REST API endpoints
│   └── errors.py        # Error handlers
├── services/            # External service integrations
│   └── omdb_api.py      # OMDb API client
├── templates/           # Jinja2 templates
├── static/              # CSS, images, etc.
└── tests/               # Unit tests (backend & frontend)
```

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- OMDb API key ([Get one here](http://www.omdbapi.com/apikey.aspx))

### Installation

1. Clone the repository
2. Create a `.env` file (see `.env.example`)
3. Add your OMDb API key to `.env`
4. Start the application:

```bash
docker-compose up --build
```

5. Access the app at http://localhost:<flask_port> (default: 5000)

For detailed Docker setup and commands, see [README_DOCKER.md](README_DOCKER.md).

## Testing

Run tests using Docker:

```bash
# Run all tests
docker-compose run --rm tests

# Run with coverage report
docker-compose run --rm tests pytest --cov=. --cov-report=html
```

## API Endpoints

- `GET /api/users` - List all users
- `GET /api/users/<user_id>/movies` - Get user's movie collection
- `POST /api/users/<user_id>/movies` - Add movie to user's collection

## Tech Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: HTML/CSS, Jinja2 templates
- **Testing**: pytest, Selenium
- **Database**: PostgreSQL (Docker) or SQLite (local)
- **Migrations**: Alembic
- **Logging**: Python logging with environment-based configuration

## Logging

Logging is configured based on the `FLASK_ENV` environment variable:

- **Development** (`FLASK_ENV=development`): All logs (DEBUG level and above) are displayed in the console
- **Production/Staging** (`FLASK_ENV=production` or other): Only warnings and errors are shown in the console; detailed error logs are written to `logs/movieweb_app.log`


