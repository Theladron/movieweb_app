"""
Unit tests for error handlers.
"""
import pytest


@pytest.mark.unit
class TestErrorHandlers:
    """Test error handler routes."""
    
    def test_404_error(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        assert b'404' in response.data or b'not found' in response.data.lower()

