from .main import main_bp
from .movie import movie_bp
from .user import user_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(user_bp)