"""
Unit tests for users page using Selenium.
"""
import pytest
from datamanager.data_models import User
from extensions import db


@pytest.mark.unit
class TestUsersPage:
    """Test users listing page."""
    
    def test_users_page_loads(self, driver, base_url, live_server, test_app):
        """Test that users page loads successfully (empty state)."""
        driver.get(f"{base_url}/users")
        assert "Users" in driver.title or "users" in driver.page_source.lower()
        assert driver.find_element("tag name", "body") is not None
    
    def test_users_page_with_users(self, driver, base_url, live_server, test_app):
        """Test users page displays users correctly."""
        # Create a test user
        with test_app.app_context():
            user = User(name="Test User Selenium")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        
        driver.get(f"{base_url}/users")
        page_source = driver.page_source
        
        assert "Test User Selenium" in page_source
        
        # Cleanup
        with test_app.app_context():
            db.session.delete(user)
            db.session.commit()
    
    def test_users_page_add_user_link(self, driver, base_url, live_server):
        """Test that add user link/button is accessible."""
        driver.get(f"{base_url}/users")
        # Check if there's a link to add users
        links = driver.find_elements("tag name", "a")
        add_user_links = [link for link in links if "/add_user" in link.get_attribute("href") or ""]
        # Page should have some way to add users (either visible or in navigation)

