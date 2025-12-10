"""
Unit tests for main routes.
"""
import pytest


@pytest.mark.unit
class TestMainRoutes:
    """Test main application routes."""
    
    def test_homepage(self, client):
        """Test homepage route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'MovieWeb App' in response.data
        assert b'Welcome to your personal Movie Library' in response.data

