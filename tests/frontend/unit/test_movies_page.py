"""
Unit tests for movies page using Selenium.
"""
import pytest
from datamanager.data_models import Movie
from extensions import db


@pytest.mark.unit
class TestMoviesPage:
    """Test movies listing page."""
    
    def test_movies_page_loads(self, driver, base_url, live_server):
        """Test that movies page loads successfully (empty state)."""
        driver.get(f"{base_url}/movies")
        assert "Movies" in driver.title or "movies" in driver.page_source.lower()
        assert driver.find_element("tag name", "body") is not None
    
    def test_movies_page_with_movies(self, driver, base_url, live_server, test_app):
        """Test movies page displays movies correctly."""
        # Create a test movie
        with test_app.app_context():
            movie = Movie(
                title="Test Movie Selenium",
                release_year=2023,
                director="Test Director",
                rating=8.5,
                poster="https://example.com/poster.jpg"
            )
            db.session.add(movie)
            db.session.commit()
            movie_id = movie.id
        
        driver.get(f"{base_url}/movies")
        page_source = driver.page_source
        
        assert "Test Movie Selenium" in page_source
        assert "2023" in page_source
        
        # Cleanup
        with test_app.app_context():
            db.session.delete(movie)
            db.session.commit()

