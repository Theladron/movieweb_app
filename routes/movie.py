import sqlalchemy
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

from datamanager import data_manager as data

movie_bp = Blueprint('movie', __name__)


@movie_bp.route('/movies')
def show_movies():
    """Display all movies in the database.

    Returns:
        Response: Rendered movies template with list of all movies, or error response.
    """
    try:
        movies = data.get_all_movies()
        return render_template('movies.html', movies=movies)
    except Exception as unexpected_error:
        return jsonify({'error': str(unexpected_error)}), 404


@movie_bp.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Add a movie to a user's collection.

    GET: Display the add movie form.
    POST: Process the form submission and add the movie to the user's collection.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        Response: Form template with success/error message, or error if user not found.
    """
    try:
        user = data.get_user(user_id)
    except (ValueError, sqlalchemy.exc.NoResultFound):
        return render_template('add_movie.html', user=None, user_id=user_id,
                               message="User not found.")
    if request.method == "POST":
        title = request.form.get('title', '').strip()

        if not title:
            return render_template('add_movie.html', user=user, user_id=user_id,
                                   message="Title is required.")

        try:
            # Attempt to add the movie
            result = data.add_movie(user_id, title)

            if result["message"] == "not_found":
                return render_template('add_movie.html', user=user, user_id=user_id,
                                       message=f"Movie '{title}' not found. Try again.")

            if result["message"] == "linked":
                return render_template('add_movie.html', user=user, user_id=user_id,
                                       message=f"Movie '{title}' is already in your list.")

            if result["message"] == "added":
                return render_template('add_movie.html', user=user, user_id=user_id,
                                       message=f"Movie '{title}' added successfully!")

        except sqlalchemy.exc.IntegrityError as db_error:
            return render_template('add_movie.html', user=user, user_id=user_id,
                                   message=f"Database constraint violated: {str(db_error)}")

        except sqlalchemy.exc.SQLAlchemyError as db_error:
            return render_template('add_movie.html', user=user, user_id=user_id,
                                   message=f"An unexpected database error occurred: {str(db_error)}")

        except ValueError as value_error:
            return render_template('add_movie.html', user=user, user_id=user_id,
                                   message=f"A database error occurred: {str(value_error)}")

        except Exception as unexpected_error:
            return render_template('add_movie.html', user=user, user_id=user_id,
                                   message=f"An unexpected error occurred: {str(unexpected_error)}")

    return render_template('add_movie.html', user=user, user_id=user_id)


@movie_bp.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update a user's rating for a movie.

    GET: Display the update movie rating form.
    POST: Process the form submission and update the user's rating.

    Args:
        user_id: The unique identifier of the user.
        movie_id: The unique identifier of the movie.

    Returns:
        Response: Rendered update_movie template with success/error message.
    """
    try:
        movie = data.get_movie(movie_id)
        # Get the current user_rating for this user-movie combination
        current_user_rating = data.get_user_movie_rating(user_id, movie_id)
    except sqlalchemy.exc.NoResultFound:
        return render_template('update_movie.html', movie=None,
                               message="Movie not found.", user_id=user_id)
    except ValueError as value_error:
        return render_template('update_movie.html', movie=None,
                               message=str(value_error), user_id=user_id)
    
    if request.method == "POST":
        user_rating_input = request.form.get('rating', '').strip()
        if not user_rating_input:
            return render_template('update_movie.html', movie=movie,
                                   user_id=user_id, user_rating=current_user_rating,
                                   message="Rating is required.")

        try:
            # Check if the rating is a valid float
            user_rating_float = float(user_rating_input)

            # Validate rating range
            if not (0 <= user_rating_float <= 10):
                warning_message = "Rating must be between 0 and 10."
                return render_template('update_movie.html', movie=movie,
                                       warning_message=warning_message, 
                                       user_id=user_id, user_rating=current_user_rating)
        except ValueError:
            return render_template('update_movie.html', movie=movie,
                                   user_id=user_id, user_rating=current_user_rating,
                                   message="Invalid rating. Please enter "
                                            "a valid number between 0 and 10.")

        try:
            data.update_movie(movie_id=movie_id, user_id=user_id, rating=user_rating_float)
            # Update current_user_rating after successful update
            current_user_rating = user_rating_float
        except ValueError as value_error:
            return render_template('update_movie.html', movie=movie,
                                   user_id=user_id, user_rating=current_user_rating,
                                   message=str(value_error))
        except Exception as unexpected_error:
            return render_template('update_movie.html', movie=movie,
                                   user_id=user_id, user_rating=current_user_rating,
                                   message=f"An error occurred while "
                                            f"updating the movie: {str(unexpected_error)}.")

        return render_template('update_movie.html', movie=movie,
                               user_id=user_id, user_rating=current_user_rating,
                               message="Rating updated successfully!")

    return render_template('update_movie.html', movie=movie, user_id=user_id, 
                          user_rating=current_user_rating)


@movie_bp.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):
    """Delete a movie from a user's collection.

    If no other users have the movie, deletes it from the database entirely.

    Args:
        user_id: The unique identifier of the user.
        movie_id: The unique identifier of the movie to delete.

    Returns:
        Response: Redirect to user's movies page with success/error message.
    """
    try:
        movie_to_delete = data.delete_movie(user_id, movie_id)
        if not movie_to_delete:
            return redirect(url_for('user.user_movies', user_id=user_id,
                                    message="Movie not found."))

        return redirect(url_for('user.user_movies', user_id=user_id,
                                message="Movie deleted successfully."))
    except Exception as unexpected_error:
        return redirect(url_for('user.user_movies', user_id=user_id,
                                message=f"An error occurred: {str(unexpected_error)}"))
