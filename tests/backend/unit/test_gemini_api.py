"""
Unit tests for Gemini API service.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from services.gemini_api import get_similar_movies, _extract_movies_from_text


@pytest.mark.unit
class TestGeminiAPI:
    """Test Gemini API service."""
    
    @patch('services.gemini_api.GEMINI_AVAILABLE', True)
    @patch('services.gemini_api.GEMINI_API_KEY', 'test-key')
    @patch('services.gemini_api.genai')
    def test_get_similar_movies_success(self, mock_genai):
        """Test successful movie recommendations."""
        # Mock the GenerativeModel and response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '["The Matrix Reloaded", "Inception", "Blade Runner 2049", "Ex Machina", "Ghost in the Shell"]'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        result = get_similar_movies("The Matrix")
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 5
        assert "The Matrix Reloaded" in result
        mock_model.generate_content.assert_called_once()
    
    @patch('services.gemini_api.GEMINI_AVAILABLE', True)
    @patch('services.gemini_api.GEMINI_API_KEY', 'test-key')
    @patch('services.gemini_api.genai')
    def test_get_similar_movies_with_markdown(self, mock_genai):
        """Test parsing response with markdown code blocks."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '```json\n["Movie 1", "Movie 2", "Movie 3", "Movie 4", "Movie 5"]\n```'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        result = get_similar_movies("Test Movie")
        
        assert result is not None
        assert len(result) == 5
        assert "Movie 1" in result
    
    @patch('services.gemini_api.GEMINI_AVAILABLE', True)
    @patch('services.gemini_api.GEMINI_API_KEY', 'test-key')
    @patch('services.gemini_api.genai')
    def test_get_similar_movies_text_extraction(self, mock_genai):
        """Test fallback to text extraction when JSON parsing fails."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        # Simulate non-JSON response
        mock_response.text = '1. Movie Title One\n2. Movie Title Two\n3. Movie Title Three'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        result = get_similar_movies("Test Movie")
        
        # Should extract movies from numbered list
        assert result is not None
        assert len(result) >= 3
    
    @patch('services.gemini_api.GEMINI_AVAILABLE', True)
    @patch('services.gemini_api.GEMINI_API_KEY', None)
    def test_get_similar_movies_no_api_key(self):
        """Test that None is returned when API key is not set."""
        result = get_similar_movies("Test Movie")
        assert result is None
    
    @patch('services.gemini_api.GEMINI_AVAILABLE', False)
    def test_get_similar_movies_package_not_available(self):
        """Test that None is returned when google-generativeai is not installed."""
        result = get_similar_movies("Test Movie")
        assert result is None
    
    def test_get_similar_movies_empty_title(self):
        """Test that None is returned for empty title."""
        result = get_similar_movies("")
        assert result is None
        
        result = get_similar_movies(None)
        assert result is None
    
    @patch('services.gemini_api.GEMINI_AVAILABLE', True)
    @patch('services.gemini_api.GEMINI_API_KEY', 'test-key')
    @patch('services.gemini_api.genai')
    def test_get_similar_movies_api_error(self, mock_genai_module):
        """Test handling of API errors."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai_module.GenerativeModel.return_value = mock_model
        
        result = get_similar_movies("Test Movie")
        assert result is None


@pytest.mark.unit
class TestMovieExtraction:
    """Test movie title extraction from text."""
    
    def test_extract_movies_from_quoted_strings(self):
        """Test extracting movie titles from quoted strings."""
        text = 'Here are some movies: "Movie One", "Movie Two", and "Movie Three"'
        result = _extract_movies_from_text(text)
        assert result is not None
        assert len(result) >= 3
        assert "Movie One" in result
    
    def test_extract_movies_from_numbered_list(self):
        """Test extracting movie titles from numbered list."""
        text = '1. First Movie\n2. Second Movie\n3. Third Movie'
        result = _extract_movies_from_text(text)
        assert result is not None
        assert len(result) >= 3
    
    def test_extract_movies_no_matches(self):
        """Test that None is returned when no movies can be extracted."""
        text = 'This is just some random text with no movie titles.'
        result = _extract_movies_from_text(text)
        # Should return None or empty list when no patterns match
        assert result is None or len(result) == 0
    
    def test_extract_movies_removes_duplicates(self):
        """Test that duplicate movie titles are removed."""
        text = '"Movie Title" and "Movie Title" and "Another Movie"'
        result = _extract_movies_from_text(text)
        assert result is not None
        assert result.count("Movie Title") == 1

