from flask import Blueprint, render_template, jsonify
from managers import data_manager as data

movie_bp = Blueprint('movie', __name__)

@movie_bp.route('/movies')
def show_movies():
    try:
        movies = data.get_all_movies()
        return render_template('movies.html', movies=movies)
    except Exception as error:
        return jsonify({'error': str(error)}), 404
