from .main import main_bp
from .movie import movie_bp
from .user import user_bp

def register_blueprints(app):
    """Registers the blueprints for the main, movie, and user routes."""
    app.register_blueprint(main_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(user_bp)