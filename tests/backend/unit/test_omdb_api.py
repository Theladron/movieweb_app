"""
Unit tests for OMDb API service.
"""
import pytest
from unittest.mock import patch, Mock
from services.omdb_api import fetch_movie_data
from tests.backend.fixtures.sample_data import SAMPLE_OMDB_RESPONSE, SAMPLE_OMDB_RESPONSE_NOT_FOUND


@pytest.mark.unit
class TestOMDbAPI:
    """Test OMDb API integration."""
    
    @patch('services.omdb_api.requests.get')
    def test_fetch_movie_data_success(self, mock_get):
        """Test successfully fetching movie data from OMDb API."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_OMDB_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_movie_data("The Matrix")
        
        assert result is not None
        assert result['title'] == "The Matrix"
        assert result['release_year'] == "1999"
        assert result['director'] == "Lana Wachowski, Lilly Wachowski"
        assert result['rating'] == "8.7"
        assert result['poster'] == "https://example.com/matrix.jpg"
    
    @patch('services.omdb_api.requests.get')
    def test_fetch_movie_data_not_found(self, mock_get):
        """Test handling when movie is not found in OMDb API."""
        # Mock API error response
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_OMDB_RESPONSE_NOT_FOUND
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_movie_data("NonExistentMovie")
        
        assert result is None
    
    @patch('services.omdb_api.requests.get')
    def test_fetch_movie_data_http_error(self, mock_get):
        """Test handling HTTP errors from OMDb API."""
        from requests.exceptions import HTTPError
        
        # Mock HTTP error
        mock_get.side_effect = HTTPError("404 Not Found")
        
        result = fetch_movie_data("Some Movie")
        
        assert result is None
    
    @patch('services.omdb_api.requests.get')
    def test_fetch_movie_data_connection_error(self, mock_get):
        """Test handling connection errors."""
        from requests.exceptions import ConnectionError
        
        # Mock connection error
        mock_get.side_effect = ConnectionError("Connection failed")
        
        result = fetch_movie_data("Some Movie")
        
        assert result is None
    
    @patch('services.omdb_api.requests.get')
    def test_fetch_movie_data_timeout(self, mock_get):
        """Test handling timeout errors."""
        from requests.exceptions import Timeout
        
        # Mock timeout error
        mock_get.side_effect = Timeout("Request timed out")
        
        result = fetch_movie_data("Some Movie")
        
        assert result is None
    
    @patch('services.omdb_api.requests.get')
    def test_fetch_movie_data_invalid_json(self, mock_get):
        """Test handling invalid JSON response."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_movie_data("Some Movie")
        
        assert result is None

