import os
import logging
from logging.handlers import RotatingFileHandler


def configure_database(app):
    """Configure database connection based on environment.

    Sets up PostgreSQL if DATABASE_URL starts with postgresql://,
    otherwise falls back to SQLite for local development or testing.

    Args:
        app: The Flask application instance to configure.
    """
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgresql://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
    else:
        # Use DATABASE_URL if set (for tests with temp SQLite), otherwise fall back to default SQLite
        if database_url and database_url.startswith('sqlite:///'):
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        else:
            # Fallback to SQLite for local development
            basedir = os.path.abspath(os.path.dirname(__file__))
            data_folder = os.path.join(basedir, 'data')
            os.makedirs(data_folder, exist_ok=True)
            db_file = os.path.join(data_folder, 'movies.db')
            app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def setup_logging(app):
    """Configure logging based on environment.

    Development mode: Shows all logs (DEBUG level) to console.
    Production/Staging mode: Only shows WARNING and above to console,
    detailed error logs are written to file.

    Args:
        app: The Flask application instance to configure logging for.
    """
    base_directory = os.path.abspath(os.path.dirname(__file__))
    flask_environment = os.getenv('FLASK_ENV', 'development')
    
    if flask_environment == 'development':
        # Development: Verbose console logging
        app.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
    else:
        # Production/Staging: Minimal console output, log errors to file
        app.logger.setLevel(logging.WARNING)
        
        # Console handler: Only warnings and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        app.logger.addHandler(console_handler)
        
        # File handler: Log errors to file
        log_directory = os.path.join(base_directory, 'logs')
        if not os.path.exists(log_directory):
            os.mkdir(log_directory)
        file_handler = RotatingFileHandler(
            os.path.join(log_directory, 'movieweb_app.log'),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.ERROR)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        app.logger.addHandler(file_handler)
    
    # Suppress noisy logs from third-party libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

