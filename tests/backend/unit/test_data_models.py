"""
Unit tests for data models.
"""
import pytest
from datamanager.data_models import User, Movie, UserMovies


@pytest.mark.unit
class TestUserModel:
    """Test User model."""
    
    def test_create_user(self, app):
        """Test creating a user instance."""
        with app.app_context():
            user = User(name="Test User")
            assert user.name == "Test User"
            assert user.id is None  # Not yet persisted


@pytest.mark.unit
class TestMovieModel:
    """Test Movie model."""
    
    def test_create_movie(self, app):
        """Test creating a movie instance."""
        with app.app_context():
            movie = Movie(
                title="The Matrix",
                release_year=1999,
                director="Lana Wachowski",
                rating=8.7,
                poster="https://example.com/poster.jpg"
            )
            assert movie.title == "The Matrix"
            assert movie.release_year == 1999
            assert movie.rating == 8.7


@pytest.mark.unit
class TestUserMoviesModel:
    """Test UserMovies linking table model."""
    
    def test_create_user_movies(self, app, sample_user, sample_movie):
        """Test creating a user-movie link."""
        with app.app_context():
            user_movie = UserMovies(
                user_id=sample_user.id,
                movie_id=sample_movie.id,
                user_rating=9.0
            )
            assert user_movie.user_id == sample_user.id
            assert user_movie.movie_id == sample_movie.id
            assert user_movie.user_rating == 9.0
    
    def test_user_movies_optional_rating(self, app, sample_user, sample_movie):
        """Test that user_rating can be None."""
        with app.app_context():
            user_movie = UserMovies(
                user_id=sample_user.id,
                movie_id=sample_movie.id,
                user_rating=None
            )
            assert user_movie.user_rating is None

