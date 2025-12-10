"""
Unit tests for API routes.
"""
import pytest
import json
from datamanager.data_models import User, Movie, UserMovies
from extensions import db
from datamanager import data_manager


@pytest.mark.unit
class TestAPIUsers:
    """Test API /api/users endpoint."""
    
    def test_list_users_empty(self, client):
        """Test listing users when database is empty."""
        response = client.get('/api/users')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['users'] == []
        assert data['count'] == 0
    
    def test_list_users(self, client, sample_user):
        """Test listing users."""
        response = client.get('/api/users')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['users']) == 1
        assert data['users'][0]['id'] == sample_user.id
        assert data['users'][0]['name'] == sample_user.name
        assert data['count'] == 1


@pytest.mark.unit
class TestAPIUserMovies:
    """Test API /api/users/<user_id>/movies endpoints."""
    
    def test_get_user_movies_empty(self, client, sample_user):
        """Test getting movies for a user with no movies."""
        response = client.get(f'/api/users/{sample_user.id}/movies')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['user_id'] == sample_user.id
        assert data['user_name'] == sample_user.name
        assert data['movies'] == []
        assert data['count'] == 0
    
    def test_get_user_movies(self, client, sample_user, sample_movie, sample_user_movie):
        """Test getting movies for a user."""
        response = client.get(f'/api/users/{sample_user.id}/movies')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['user_id'] == sample_user.id
        assert len(data['movies']) == 1
        assert data['movies'][0]['id'] == sample_movie.id
        assert data['movies'][0]['title'] == sample_movie.title
        assert data['movies'][0]['user_rating'] == 9.0
        assert data['count'] == 1
    
    def test_get_user_movies_not_found(self, client):
        """Test getting movies for non-existent user."""
        response = client.get('/api/users/999/movies')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    @pytest.mark.parametrize('method', ['POST'])
    def test_add_user_movie_no_json(self, client, sample_user, method):
        """Test adding movie without JSON body."""
        if method == 'POST':
            response = client.post(
                f'/api/users/{sample_user.id}/movies',
                data='not json',
                content_type='application/json'
            )
            assert response.status_code == 400
    
    def test_add_user_movie_missing_title(self, client, sample_user):
        """Test adding movie without title field."""
        response = client.post(
            f'/api/users/{sample_user.id}/movies',
            json={},
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Title is required' in data['error']
    
    def test_add_user_movie_empty_title(self, client, sample_user):
        """Test adding movie with empty title."""
        response = client.post(
            f'/api/users/{sample_user.id}/movies',
            json={'title': ''},
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Title is required' in data['error']
    
    def test_add_user_movie_user_not_found(self, client):
        """Test adding movie for non-existent user."""
        response = client.post(
            '/api/users/999/movies',
            json={'title': 'Test Movie'},
            content_type='application/json'
        )
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

