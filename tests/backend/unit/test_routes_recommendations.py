"""
Unit tests for movie recommendations API route.
"""
import pytest
import json
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestMovieRecommendationsRoute:
    """Test /api/movies/recommendations endpoint."""
    
    def test_get_recommendations_success(self, client):
        """Test successful movie recommendations request."""
        mock_recommendations = ["Movie 1", "Movie 2", "Movie 3", "Movie 4", "Movie 5"]
        
        with patch('routes.api.get_similar_movies', return_value=mock_recommendations):
            response = client.get('/api/movies/recommendations?title=The Matrix')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['original_movie'] == 'The Matrix'
            assert data['recommendations'] == mock_recommendations
            assert data['count'] == 5
    
    def test_get_recommendations_missing_title(self, client):
        """Test recommendations request without title parameter."""
        response = client.get('/api/movies/recommendations')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'title' in data['error'].lower()
    
    def test_get_recommendations_empty_title(self, client):
        """Test recommendations request with empty title."""
        response = client.get('/api/movies/recommendations?title=')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_recommendations_api_failure(self, client):
        """Test recommendations request when Gemini API returns None."""
        with patch('routes.api.get_similar_movies', return_value=None):
            response = client.get('/api/movies/recommendations?title=The Matrix')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'error' in data
    
    def test_get_recommendations_empty_list(self, client):
        """Test recommendations request when API returns empty list."""
        with patch('routes.api.get_similar_movies', return_value=[]):
            response = client.get('/api/movies/recommendations?title=The Matrix')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'No recommendations' in data['error']
    
    def test_get_recommendations_exception(self, client):
        """Test recommendations request when exception occurs."""
        with patch('routes.api.get_similar_movies', side_effect=Exception("API Error")):
            response = client.get('/api/movies/recommendations?title=The Matrix')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'error' in data

