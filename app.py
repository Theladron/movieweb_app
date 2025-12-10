import os

from dotenv import load_dotenv
from flask import Flask

from db_validator import validate_database
from extensions import db
from managers import data_manager
from routes import register_blueprints

load_dotenv()


def create_app():
    """
    Creates and configures the Flask application, calls for
    database validation and blueprint registration.
    """
    app = Flask(__name__)

    # Use PostgreSQL if DATABASE_URL is set, otherwise fall back to SQLite
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
    else:
        # Fallback to SQLite for local development
        basedir = os.path.abspath(os.path.dirname(__file__))
        data_folder = os.path.join(basedir, 'data')
        os.makedirs(data_folder, exist_ok=True)
        db_file = os.path.join(data_folder, 'movies.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    data_manager.init_app(app)  # initialize with app here

    # Only validate database if not using PostgreSQL (Alembic handles migrations for PostgreSQL)
    if not database_url:
        validate_database(app)
    
    register_blueprints(app)

    # Ensure static files (CSS) load properly to prevent FOUC
    @app.after_request
    def add_header(response):
        # Add headers to prevent premature rendering
        if response.content_type and 'text/html' in response.content_type:
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
