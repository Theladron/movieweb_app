from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy

from datamanager import data_manager as data
from services.gemini_api import get_similar_movies

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/users', methods=['GET'])
def list_users():
    """List all users in the system.

    Returns:
        Response: JSON response with list of users and count, or error message.
    """
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
    except Exception as unexpected_error:
        return jsonify({
            'success': False,
            'error': str(unexpected_error)
        }), 500


@api_bp.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    """List a user's favorite movies (movie collection).

    Args:
        user_id: The unique identifier of the user.

    Returns:
        Response: JSON response with user's movies and count, or error message.
    """
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
    except ValueError as value_error:
        return jsonify({
            'success': False,
            'error': str(value_error)
        }), 404
    except Exception as unexpected_error:
        return jsonify({
            'success': False,
            'error': str(unexpected_error)
        }), 500


@api_bp.route('/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    """Add a new favorite movie to a user's collection.

    Args:
        user_id: The unique identifier of the user.

    Request Body:
        JSON with 'title' field containing the movie title.

    Returns:
        Response: JSON response with success status and movie data, or error message.
    """
    try:
        # Verify user exists
        user = data.get_user(user_id)
        
        # Get movie title from request - handle invalid JSON
        # get_json() with silent=True returns None for invalid JSON instead of raising exception
        json_request_data = request.get_json(silent=True)
        
        # If get_json() returns None, it means no JSON data or invalid JSON was sent
        if json_request_data is None:
            return jsonify({
                'success': False,
                'error': 'Request body must be valid JSON'
            }), 400
        
        # Check for title field in request data
        if 'title' not in json_request_data:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        movie_title = json_request_data.get('title', '').strip()
        if not movie_title:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        # Add movie using existing data manager method
        add_movie_result = data.add_movie(user_id, movie_title)
        
        if add_movie_result["message"] == "not_found":
            return jsonify({
                'success': False,
                'error': f"Movie '{movie_title}' not found"
            }), 404
        
        if add_movie_result["message"] == "linked":
            return jsonify({
                'success': False,
                'error': f"Movie '{movie_title}' is already in user's favorites"
            }), 409
        
        if add_movie_result["message"] == "added":
            added_movie = add_movie_result["movie"]
            return jsonify({
                'success': True,
                'message': f"Movie '{movie_title}' added successfully",
                'movie': {
                    'id': added_movie.id,
                    'title': added_movie.title,
                    'release_year': added_movie.release_year,
                    'director': added_movie.director,
                    'rating': added_movie.rating,
                    'poster': added_movie.poster
                }
            }), 201
        
        return jsonify({
            'success': False,
            'error': 'Unknown error occurred'
        }), 500
        
    except ValueError as value_error:
        return jsonify({
            'success': False,
            'error': str(value_error)
        }), 404
    except BadRequest:
        # Handle invalid JSON from get_json() when silent=False (but we use silent=True, so this is fallback)
        return jsonify({
            'success': False,
            'error': 'Request body must be valid JSON'
        }), 400
    except sqlalchemy.exc.IntegrityError as integrity_error:
        return jsonify({
            'success': False,
            'error': f'Database constraint violated: {str(integrity_error)}'
        }), 400
    except Exception as unexpected_error:
        return jsonify({
            'success': False,
            'error': str(unexpected_error)
        }), 500


@api_bp.route('/movies/recommendations', methods=['GET'])
def get_movie_recommendations():
    """Get AI-powered movie recommendations based on a movie title.

    Query Parameters:
        title: The movie title to get recommendations for.

    Returns:
        Response: JSON response with recommended movies, or error message.
    """
    try:
        # Get movie title from query parameters
        movie_title = request.args.get('title', '').strip()
        
        if not movie_title:
            return jsonify({
                'success': False,
                'error': 'Movie title is required. Provide it as a query parameter: ?title=Movie Name'
            }), 400
        
        # Get recommendations from Gemini API
        recommended_movies = get_similar_movies(movie_title)
        
        if recommended_movies is None:
            # Check if it's an API key issue or another error
            import os
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            if not gemini_api_key:
                api_error_message = ('GEMINI_API_KEY is not set. Please check your .env file '
                                    'and ensure it is passed to the Docker container.')
            else:
                api_error_message = 'Failed to get movie recommendations. Check server logs for details.'
            return jsonify({
                'success': False,
                'error': api_error_message
            }), 500
        
        if len(recommended_movies) == 0:
            return jsonify({
                'success': False,
                'error': 'No recommendations found for the given movie title.'
            }), 404
        
        return jsonify({
            'success': True,
            'original_movie': movie_title,
            'recommendations': recommended_movies,
            'count': len(recommended_movies)
        }), 200
        
    except Exception as unexpected_error:
        return jsonify({
            'success': False,
            'error': str(unexpected_error)
        }), 500

