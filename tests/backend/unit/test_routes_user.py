"""
Unit tests for user routes.
"""
import pytest
from datamanager.data_models import User
from extensions import db


@pytest.mark.unit
class TestUserRoutes:
    """Test user-related routes."""
    
    def test_show_users_empty(self, client):
        """Test showing users page when database is empty."""
        response = client.get('/users')
        assert response.status_code == 200
        assert b'Users' in response.data or b'users' in response.data.lower()
    
    def test_show_users(self, client, sample_user):
        """Test showing users page with users."""
        response = client.get('/users')
        assert response.status_code == 200
        assert sample_user.name.encode() in response.data
    
    def test_get_add_user_page(self, client):
        """Test getting the add user page."""
        response = client.get('/add_user')
        assert response.status_code == 200
        assert b'Add User' in response.data or b'add' in response.data.lower()
    
    def test_post_add_user(self, client):
        """Test adding a user via POST."""
        response = client.post('/add_user', data={'name': 'New Test User'})
        assert response.status_code == 302  # Redirect after successful add
        
        # Verify user was created
        with client.application.app_context():
            user = db.session.query(User).filter_by(name='New Test User').first()
            assert user is not None
    
    def test_post_add_user_empty_name(self, client):
        """Test adding user with empty name."""
        response = client.post('/add_user', data={'name': ''})
        assert response.status_code == 200
        assert b'required' in response.data.lower() or b'Name' in response.data
    
    def test_get_user_movies(self, client, sample_user):
        """Test getting user movies page."""
        response = client.get(f'/users/{sample_user.id}')
        assert response.status_code == 200
    
    def test_get_user_movies_not_found(self, client):
        """Test getting movies for non-existent user."""
        response = client.get('/users/999')
        assert response.status_code == 200  # Route handles gracefully
        assert b'not found' in response.data.lower() or b'No user found' in response.data

