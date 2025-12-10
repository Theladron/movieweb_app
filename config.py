import os
import logging
from logging.handlers import RotatingFileHandler


def configure_database(app):
    """
    Configure database connection based on environment.
    - PostgreSQL: Used if DATABASE_URL starts with postgresql://
    - SQLite: Used for local development or testing
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
    """
    Configure logging based on environment.
    - Development: Show all logs (DEBUG level) to console
    - Production/Staging: Only show WARNING and above to console, log errors to file
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    if flask_env == 'development':
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
        log_dir = os.path.join(basedir, 'logs')
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'movieweb_app.log'),
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

