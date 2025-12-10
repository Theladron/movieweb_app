"""
Unit tests for homepage using Selenium.
"""
import pytest


@pytest.mark.unit
class TestHomepage:
    """Test homepage rendering and elements."""
    
    def test_homepage_loads(self, driver, base_url, live_server):
        """Test that homepage loads successfully with key elements."""
        driver.get(base_url)
        assert driver.title == "MovieWeb App - Your Personal Movie Library"
        
        # Verify main title is present
        title = driver.find_element("class name", "title")
        assert title is not None
        assert "MovieWeb App" in title.text
    
    def test_homepage_navigation_links(self, driver, base_url, live_server):
        """Test that navigation links are present."""
        driver.get(base_url)
        nav = driver.find_element("tag name", "nav")
        assert nav is not None
        
        # Check for navigation buttons
        buttons = nav.find_elements("tag name", "button")
        assert len(buttons) >= 3  # Home, Movies, Users
    
    def test_homepage_feature_cards(self, driver, base_url, live_server):
        """Test that feature cards are present."""
        driver.get(base_url)
        cards = driver.find_elements("class name", "home-card")
        assert len(cards) == 3  # Three feature cards
    
    def test_homepage_feature_card_content(self, driver, base_url, live_server):
        """Test that feature cards contain expected content."""
        driver.get(base_url)
        cards = driver.find_elements("class name", "home-card")
        
        expected_texts = ["Create Your Profile", "Add Movies", "Rate & Review"]
        for card in cards:
            card_text = card.text
            assert any(expected in card_text for expected in expected_texts)
    
    def test_homepage_get_started_button(self, driver, base_url, live_server):
        """Test that 'Get Started' button is present and links to users."""
        driver.get(base_url)
        cta_button = driver.find_element("class name", "cta-button")
        assert cta_button is not None
        assert cta_button.get_attribute("href") == f"{base_url}/users"

