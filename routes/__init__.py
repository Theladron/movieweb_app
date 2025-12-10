from .main import main_bp
from .movie import movie_bp
from .user import user_bp
from .errors import errors_bp
from .api import api_bp

def register_blueprints(app):
    """Registers the blueprints for the main, movie, user, errors, and API routes."""
    app.register_blueprint(main_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(api_bp)