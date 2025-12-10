"""
Unit tests for error pages using Selenium.
"""
import pytest


@pytest.mark.unit
class TestErrorPages:
    """Test error page rendering."""
    
    def test_404_page_loads(self, driver, base_url, live_server):
        """Test that 404 page loads and displays error message."""
        driver.get(f"{base_url}/nonexistent-route-12345")
        assert driver.find_element("tag name", "body") is not None
        page_source = driver.page_source.lower()
        assert "404" in driver.page_source or "not found" in page_source
    
    def test_404_page_navigation(self, driver, base_url, live_server):
        """Test that 404 page has navigation back to home."""
        driver.get(f"{base_url}/nonexistent-route")
        # Check for home link or button
        home_links = driver.find_elements("xpath", "//a[contains(@href, '/')]")
        assert len(home_links) > 0

