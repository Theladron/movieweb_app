"""
Unit tests for movie routes.
"""
import pytest
from datamanager.data_models import Movie
from extensions import db


@pytest.mark.unit
class TestMovieRoutes:
    """Test movie-related routes."""
    
    def test_show_movies_empty(self, client):
        """Test showing movies page when database is empty."""
        response = client.get('/movies')
        assert response.status_code == 200
        assert b'Movies' in response.data or b'movies' in response.data.lower()
    
    def test_show_movies(self, client, sample_movie):
        """Test showing movies page with movies."""
        response = client.get('/movies')
        assert response.status_code == 200
        assert sample_movie.title.encode() in response.data
    
    def test_get_add_movie_page(self, client, sample_user):
        """Test getting the add movie page."""
        response = client.get(f'/users/{sample_user.id}/add_movie')
        assert response.status_code == 200
        assert b'Add Movie' in response.data or b'add' in response.data.lower()
    
    def test_get_add_movie_user_not_found(self, client):
        """Test getting add movie page for non-existent user."""
        response = client.get('/users/999/add_movie')
        assert response.status_code == 200  # Route handles gracefully
        assert b'not found' in response.data.lower() or response.status_code == 404
    
    def test_get_update_movie_page(self, client, sample_user, sample_movie, sample_user_movie):
        """Test getting the update movie page."""
        response = client.get(f'/users/{sample_user.id}/update_movie/{sample_movie.id}')
        assert response.status_code == 200
        assert sample_movie.title.encode() in response.data

