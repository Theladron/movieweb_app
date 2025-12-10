import os

from dotenv import load_dotenv
from flask import Flask

from extensions import db
from datamanager import data_manager
from routes import register_blueprints
from config import setup_logging, configure_database

load_dotenv()


def create_app():
    """Create and configure the Flask application.

    Creates Flask app instance, configures database connection and logging,
    initializes extensions, and registers all blueprints.
    Database schema is handled by Alembic migrations (Docker/PostgreSQL)
    or created automatically in tests (temporary SQLite databases).

    Returns:
        Flask: Configured Flask application instance.
    """
    # Get the base directory
    base_directory = os.path.abspath(os.path.dirname(__file__))
    # Explicitly set static folder path
    static_folder_path = os.path.join(base_directory, 'static')
    app = Flask(__name__, static_folder=static_folder_path, static_url_path='/static')

    # Configure database connection
    configure_database(app)
    
    # Setup logging based on environment
    setup_logging(app)
    
    db.init_app(app)
    data_manager.init_app(app)  # initialize with app here
    
    register_blueprints(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
