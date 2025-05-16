import sqlalchemy
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

from managers import data_manager as data

movie_bp = Blueprint('movie', __name__)


@movie_bp.route('/movies')
def show_movies():
    try:
        movies = data.get_all_movies()
        return render_template('movies.html', movies=movies)
    except Exception as error:
        return jsonify({'error': str(error)}), 404


@movie_bp.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    try:
        user_name = data.get_user(user_id)
    except sqlalchemy.exc.NoResultFound:
        return render_template('add_movie.html', user=None,
                               message="User not found.")
    if request.method == "POST":
        title = request.form.get('title', '').strip()

        if not title:
            return render_template('add_movie.html', user=user_name,
                                   message="Title is required.")

        try:
            # Attempt to add the movie
            result = data.add_movie(user_id, title)

            if result["message"] == "not_found":
                return render_template('add_movie.html', user=user_name,
                                       message=f"Movie '{title}' not found. Try again.")

            if result["message"] == "linked":
                return render_template('add_movie.html', user=user_name,
                                       message=f"Movie '{title}' is already in your list.")

            if result["message"] == "added":
                return render_template('add_movie.html', user=user_name,
                                       message=f"Movie '{title}' added successfully!")

        except sqlalchemy.exc.IntegrityError as e:
            return render_template('add_movie.html', user=user_name,
                                   message=f"Database constraint violated: {str(e)}")

        except sqlalchemy.exc.SQLAlchemyError as e:
            return render_template('add_movie.html', user=user_name,
                                   message=f"An unexpected database error occurred: {str(e)}")

        except ValueError as e:
            return render_template('add_movie.html', user=user_name,
                                   message=f"A database error occurred: {str(e)}")

        except Exception as e:
            return render_template('add_movie.html', user=user_name,
                                   message=f"An unexpected error occurred: {str(e)}")

    return render_template('add_movie.html', user=user_name)


@movie_bp.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    try:
        movie = data.get_movie(movie_id)
    except sqlalchemy.exc.NoResultFound:
        return render_template('update_movie.html', movie=None,
                               message="Movie not found.")
    if request.method == "POST":
        custom_rating = request.form.get('rating').strip()
        if not custom_rating:
            return render_template('update_movie.html', movie=movie,
                                   user_id=user_id, message="Rating is required.")

        try:
            # Check if the rating is a valid float
            custom_rating = float(custom_rating)

            # Log rating range validation
            if not (0 <= custom_rating <= 10):
                warning_message = "Rating must be between 0 and 10."
                return render_template('update_movie.html', movie=movie,
                                       warning_message=warning_message, user_id=user_id)
        except ValueError:
            return render_template('update_movie.html', movie=movie,
                                   user_id=user_id, message="Invalid rating. Please enter "
                                                            "a valid number between 0 and 10.")

        try:
            data.update_movie(movie_id=movie_id, user_id=user_id, rating=custom_rating)
        except ValueError as error:
            return render_template('update_movie.html', movie=movie,
                                   user_id=user_id, message=str(error))
        except Exception as error:
            return render_template('update_movie.html', movie=movie,
                                   user_id=user_id, message=f"An error occurred while "
                                                            f"updating the movie: {str(error)}.")

        return render_template('update_movie.html', movie=movie,
                               user_id=user_id, message="Rating updated successfully!")

    return render_template('update_movie.html', movie=movie, user_id=user_id)


@movie_bp.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):
    try:
        movie_to_delete = data.delete_movie(user_id, movie_id)
        if not movie_to_delete:
            return redirect(url_for('user.user_movies', user_id=user_id,
                                    message="Movie not found."))

        return redirect(url_for('user.user_movies', user_id=user_id,
                                message="Movie deleted successfully."))
    except Exception as error:
        return redirect(url_for('user.user_movies', user_id=user_id,
                                message=f"An error occurred: {str(error)}"))
