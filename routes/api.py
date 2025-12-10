from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy

from datamanager import data_manager as data
from services.gemini_api import get_similar_movies

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/users', methods=['GET'])
def list_users():
    """List all users"""
    try:
        users = data.get_all_users()
        users_list = [
            {
                'id': user.id,
                'name': user.name
            }
            for user in users
        ]
        return jsonify({
            'success': True,
            'users': users_list,
            'count': len(users_list)
        }), 200
    except Exception as error:
        return jsonify({
            'success': False,
            'error': str(error)
        }), 500


@api_bp.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    """List a user's favorite movies"""
    try:
        # Verify user exists
        user = data.get_user(user_id)
        
        # Get user's movies
        movies = data.get_user_movies(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'user_name': user.name,
            'movies': movies,
            'count': len(movies)
        }), 200
    except ValueError as error:
        return jsonify({
            'success': False,
            'error': str(error)
        }), 404
    except Exception as error:
        return jsonify({
            'success': False,
            'error': str(error)
        }), 500


@api_bp.route('/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    """Add a new favorite movie for a user"""
    try:
        # Verify user exists
        user = data.get_user(user_id)
        
        # Get movie title from request - handle invalid JSON
        # Try to parse JSON - get_json() with silent=True returns None for invalid JSON
        try:
            request_data = request.get_json(silent=True)
        except (BadRequest, TypeError, ValueError):
            return jsonify({
                'success': False,
                'error': 'Request body must be valid JSON'
            }), 400
        
        # If get_json() returns None, it means no JSON data or invalid JSON was sent
        if request_data is None:
            return jsonify({
                'success': False,
                'error': 'Request body must be valid JSON'
            }), 400
        
        # Check for title field
        if 'title' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        title = request_data.get('title', '').strip()
        if not title:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        # Add movie using existing data manager method
        result = data.add_movie(user_id, title)
        
        if result["message"] == "not_found":
            return jsonify({
                'success': False,
                'error': f"Movie '{title}' not found"
            }), 404
        
        if result["message"] == "linked":
            return jsonify({
                'success': False,
                'error': f"Movie '{title}' is already in user's favorites"
            }), 409
        
        if result["message"] == "added":
            movie = result["movie"]
            return jsonify({
                'success': True,
                'message': f"Movie '{title}' added successfully",
                'movie': {
                    'id': movie.id,
                    'title': movie.title,
                    'release_year': movie.release_year,
                    'director': movie.director,
                    'rating': movie.rating,
                    'poster': movie.poster
                }
            }), 201
        
        return jsonify({
            'success': False,
            'error': 'Unknown error occurred'
        }), 500
        
    except ValueError as error:
        return jsonify({
            'success': False,
            'error': str(error)
        }), 404
    except BadRequest:
        # Handle invalid JSON from get_json() when silent=False (but we use silent=True, so this is fallback)
        return jsonify({
            'success': False,
            'error': 'Request body must be valid JSON'
        }), 400
    except sqlalchemy.exc.IntegrityError as error:
        return jsonify({
            'success': False,
            'error': f'Database constraint violated: {str(error)}'
        }), 400
    except Exception as error:
        return jsonify({
            'success': False,
            'error': str(error)
        }), 500


@api_bp.route('/movies/recommendations', methods=['GET'])
def get_movie_recommendations():
    """Get AI-powered movie recommendations based on a movie title."""
    try:
        # Get movie title from query parameters
        movie_title = request.args.get('title', '').strip()
        
        if not movie_title:
            return jsonify({
                'success': False,
                'error': 'Movie title is required. Provide it as a query parameter: ?title=Movie Name'
            }), 400
        
        # Get recommendations from Gemini API
        recommendations = get_similar_movies(movie_title)
        
        if recommendations is None:
            # Check if it's an API key issue or another error
            import os
            if not os.getenv('GEMINI_API_KEY'):
                error_msg = 'GEMINI_API_KEY is not set. Please check your .env file and ensure it is passed to the Docker container.'
            else:
                error_msg = 'Failed to get movie recommendations. Check server logs for details.'
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
        if len(recommendations) == 0:
            return jsonify({
                'success': False,
                'error': 'No recommendations found for the given movie title.'
            }), 404
        
        return jsonify({
            'success': True,
            'original_movie': movie_title,
            'recommendations': recommendations,
            'count': len(recommendations)
        }), 200
        
    except Exception as error:
        return jsonify({
            'success': False,
            'error': str(error)
        }), 500

