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
│   ├── omdb_api.py      # OMDb API client
│   └── gemini_api.py    # Google Gemini API client (AI recommendations)
├── templates/           # Jinja2 templates
├── static/              # CSS, images, etc.
└── tests/               # Unit tests (backend & frontend)
```

## Quick Start (SQLite-first)

### Prerequisites

- Python 3.11+
- OMDb API key ([Get one here](http://www.omdbapi.com/apikey.aspx))
- Gemini API key (optional, for AI movie recommendations) ([Get one here](https://ai.google.dev/))

### Installation (local or PythonAnywhere-friendly)

1. Clone the repository
2. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file (see `.env.example` if present) and set:
   - `OMDB_API_KEY` (required)
   - `GEMINI_API_KEY` (optional, for AI recommendations)
   - `FLASK_ENV=production` (recommended for hosted environments)
5. Run database migrations (SQLite file lives in `data/movies.db`)
   ```bash
   mkdir -p data
   alembic upgrade head
   ```
   If you skip this step, the app will create tables lazily on first run when using SQLite.
6. Start the app
   ```bash
   python app.py
   ```
7. Access the app at http://localhost:5000

## Testing

Run tests locally:

```bash
pytest tests/ -v
```

## API Endpoints

- `GET /api/users` - List all users
- `GET /api/users/<user_id>/movies` - Get user's movie collection
- `POST /api/users/<user_id>/movies` - Add movie to user's collection
- `GET /api/movies/recommendations?title=Movie Title` - Get AI-powered movie recommendations based on a movie title

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML/CSS, Jinja2 templates
- **Testing**: pytest, Selenium
- **Database**: SQLite (default, file at `data/movies.db`)
- **Migrations**: Alembic (works with SQLite)
- **Logging**: Python logging with environment-based configuration

## Logging

Logging is configured based on the `FLASK_ENV` environment variable:

- **Development** (`FLASK_ENV=development`): All logs (DEBUG level and above) are displayed in the console
- **Production/Staging** (`FLASK_ENV=production` or other): Only warnings and errors are shown in the console; detailed error logs are written to `logs/movieweb_app.log`


