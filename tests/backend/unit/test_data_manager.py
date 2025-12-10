"""
Unit tests for SQLiteDataManager.
"""
import pytest
from datamanager.data_models import User, Movie, UserMovies
from extensions import db
from datamanager import data_manager


@pytest.mark.unit
class TestDataManagerUsers:
    """Test user-related methods in SQLiteDataManager."""
    
    def test_get_all_users_empty(self, app):
        """Test getting all users when database is empty."""
        with app.app_context():
            users = data_manager.get_all_users()
            assert users == []
    
    def test_add_user(self, app):
        """Test adding a user."""
        with app.app_context():
            user_name = data_manager.add_user("Test User")
            assert user_name == "Test User"
            
            users = data_manager.get_all_users()
            assert len(users) == 1
            assert users[0].name == "Test User"
    
    def test_add_user_empty_name(self, app):
        """Test adding a user with empty name raises ValueError."""
        with app.app_context():
            with pytest.raises(ValueError, match="User name cannot be empty"):
                data_manager.add_user("")
    
    def test_get_user(self, app, sample_user):
        """Test getting a user by ID."""
        with app.app_context():
            user = data_manager.get_user(sample_user.id)
            assert user.id == sample_user.id
            assert user.name == sample_user.name
    
    def test_get_user_not_found(self, app):
        """Test getting a non-existent user raises ValueError."""
        with app.app_context():
            with pytest.raises(ValueError, match="No user found with ID"):
                data_manager.get_user(999)
    
    def test_update_user(self, app, sample_user):
        """Test updating a user's name."""
        with app.app_context():
            result = data_manager.update_user(sample_user.id, "Updated Name")
            assert "updated successfully" in result.lower()
            
            updated_user = data_manager.get_user(sample_user.id)
            assert updated_user.name == "Updated Name"
    
    def test_delete_user(self, app, sample_user):
        """Test deleting a user."""
        with app.app_context():
            user_name = data_manager.delete_user(sample_user.id)
            assert user_name == sample_user.name
            
            with pytest.raises(ValueError):
                data_manager.get_user(sample_user.id)


@pytest.mark.unit
class TestDataManagerMovies:
    """Test movie-related methods in SQLiteDataManager."""
    
    def test_get_all_movies_empty(self, app):
        """Test getting all movies when database is empty."""
        with app.app_context():
            movies = data_manager.get_all_movies()
            assert movies == []
    
    def test_get_movie(self, app, sample_movie):
        """Test getting a movie by ID."""
        with app.app_context():
            movie = data_manager.get_movie(sample_movie.id)
            assert movie.id == sample_movie.id
            assert movie.title == sample_movie.title
    
    def test_get_movie_not_found(self, app):
        """Test getting a non-existent movie raises ValueError."""
        with app.app_context():
            with pytest.raises(ValueError, match="No movie found with ID"):
                data_manager.get_movie(999)
    
    def test_get_user_movies_empty(self, app, sample_user):
        """Test getting movies for a user with no movies."""
        with app.app_context():
            movies = data_manager.get_user_movies(sample_user.id)
            assert movies == []
    
    def test_get_user_movies(self, app, sample_user, sample_movie, sample_user_movie):
        """Test getting movies for a user."""
        with app.app_context():
            movies = data_manager.get_user_movies(sample_user.id)
            assert len(movies) == 1
            assert movies[0]['id'] == sample_movie.id
            assert movies[0]['title'] == sample_movie.title
            assert movies[0]['user_rating'] == 9.0
    
    def test_get_user_movie_rating(self, app, sample_user, sample_movie, sample_user_movie):
        """Test getting a user's rating for a movie."""
        with app.app_context():
            rating = data_manager.get_user_movie_rating(sample_user.id, sample_movie.id)
            assert rating == 9.0
    
    def test_get_user_movie_rating_not_found(self, app, sample_user, sample_movie):
        """Test getting rating for a movie user hasn't added."""
        with app.app_context():
            rating = data_manager.get_user_movie_rating(sample_user.id, sample_movie.id)
            assert rating is None


@pytest.mark.unit
class TestDataManagerUpdateMovie:
    """Test updating user movie ratings."""
    
    def test_update_movie_rating(self, app, sample_user, sample_movie, sample_user_movie):
        """Test updating a user's movie rating."""
        with app.app_context():
            data_manager.update_movie(sample_movie.id, sample_user.id, 8.5)
            
            rating = data_manager.get_user_movie_rating(sample_user.id, sample_movie.id)
            assert rating == 8.5
    
    def test_update_movie_not_found(self, app, sample_user):
        """Test updating rating for a movie user hasn't added."""
        with app.app_context():
            with pytest.raises(ValueError, match="User has not added movie"):
                data_manager.update_movie(999, sample_user.id, 8.0)

