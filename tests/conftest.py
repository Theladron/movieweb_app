"""
Root conftest.py with shared fixtures for all tests.
"""
import os
import pytest
import tempfile
from app import create_app
from extensions import db
from datamanager.data_models import User, Movie, UserMovies


@pytest.fixture(scope='function')
def app():
    """Create a Flask application instance for testing."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Set DATABASE_URL before creating app to ensure it uses our test database
    # We use the temp file path directly as SQLite URI
    old_db_url = os.environ.get('DATABASE_URL', None)
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'  # Set test database URI
    
    try:
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        # Ensure models are imported so db.create_all() can see them
        from datamanager.data_models import User, Movie, UserMovies
        
        # Create all tables
        with app.app_context():
            db.drop_all()  # Drop any existing tables first
            db.create_all()  # Create all tables
        
        yield app
        
        # Cleanup
        with app.app_context():
            db.session.remove()
            db.drop_all()
    finally:
        # Restore original DATABASE_URL
        if old_db_url is not None:
            os.environ['DATABASE_URL'] = old_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Provide a database session for tests."""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(name="Test User")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_movie(db_session):
    """Create a sample movie for testing."""
    movie = Movie(
        title="The Matrix",
        release_year=1999,
        director="Lana Wachowski, Lilly Wachowski",
        rating=8.7,
        poster="https://example.com/poster.jpg"
    )
    db_session.add(movie)
    db_session.commit()
    return movie


@pytest.fixture
def sample_user_movie(db_session, sample_user, sample_movie):
    """Create a sample user-movie link for testing."""
    user_movie = UserMovies(
        user_id=sample_user.id,
        movie_id=sample_movie.id,
        user_rating=9.0
    )
    db_session.add(user_movie)
    db_session.commit()
    return user_movie

