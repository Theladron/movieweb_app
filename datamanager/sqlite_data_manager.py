from sqlalchemy.exc import SQLAlchemyError

from datamanager.data_manager_interface import DataManagerInterface
from datamanager.data_models import User, Movie, UserMovies
from extensions import db
from services.omdb_api import fetch_movie_data


class SQLiteDataManager(DataManagerInterface):
    def __init__(self):
        self.db = db
        self.db_path = None

    def init_app(self, app):
        self.db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///movies.db")

    def get_all_users(self):
        try:
            return self.db.session.query(User).all()
        except SQLAlchemyError as error:
            print(f"Error fetching users: {error}")
            return []

    def get_all_movies(self):
        try:
            return self.db.session.query(Movie).all()
        except SQLAlchemyError as error:
            print(f"Error fetching movies: {error}")
            return []

    def get_user_movies(self, user_id):
        try:
            movies = (
                self.db.session.query(Movie)
                .join(UserMovies, UserMovies.movie_id == Movie.id)
                .filter(UserMovies.user_id == user_id)
                .all()
            )
            return movies
        except SQLAlchemyError as error:
            print(f"Error fetching user movies: {error}")
            return []

    def get_user(self, user_id):
        try:
            user = (self.db.session.query(User).filter(User.id == user_id).one_or_none())
            if not user:
                raise ValueError(f"No user found with ID {user_id}")
            return user
        except SQLAlchemyError as error:
            print(f"Error fetching user with ID {user_id}: {error}")
            return

    def add_user(self, user_name):
        if not user_name:
            raise ValueError("User name cannot be empty")
        new_user = User(name=user_name)
        self.db.session.add(new_user)
        self.db.session.commit()
        return user_name

    def update_user(self, user_id, user_name):
        try:
            updated_user = self.get_user(user_id)
            if not updated_user:
                return f"User with ID {user_id} does not exist."

            updated_user.name = user_name
            self.db.session.commit()
            return f"User '{user_name}' was updated successfully!"

        except SQLAlchemyError as error:
            self.db.session.rollback()
            raise ValueError(f"Could not update user with ID {user_id}; {error}")

    def delete_user(self, user_id):
        try:
            user_to_delete = self.get_user(user_id)
            if not user_to_delete:
                return None

            # Get all movie IDs associated with the user
            user_movies = self.db.session.query(UserMovies).filter_by(user_id=user_id).all()
            movie_ids = [user_movie.movie_id for user_movie in user_movies]

            # Delete the user's entries in UserMovies
            self.db.session.query(UserMovies).filter_by(user_id=user_id).delete()

            # Delete the user
            user_name = user_to_delete.name
            self.db.session.delete(user_to_delete)
            self.db.session.commit()

            for movie_id in movie_ids:
                other_links = self.db.session.query(UserMovies).filter_by(movie_id=movie_id).first()
                if not other_links:
                    self.db.session.query(Movie).filter_by(id=movie_id).delete()

            self.db.session.commit()

            return user_name

        except SQLAlchemyError as error:
            self.db.session.rollback()
            raise ValueError(f"Error occurred while deleting user with ID {user_id}: {error}")

    def get_user_by_name(self, user_name):
        try:
            user = self.db.session.query(User).filter(User.name == user_name).one_or_none()
            return user
        except SQLAlchemyError as error:
            raise SQLAlchemyError(f"Error fetching user by name: {error}")

    def get_movie(self, movie_id):
        try:
            movie = self.db.session.query(Movie).filter(Movie.id == movie_id).one_or_none()
            if not movie:
                raise ValueError(f"No movie found with ID {movie_id}")
            return movie
        except SQLAlchemyError as error:
            raise SQLAlchemyError(f"Error fetching movie with ID {movie_id}: {error}")

    def add_movie(self, user_id, title):

        # Fetch movie data from OMDb
        movie_data = fetch_movie_data(title)
        if not movie_data:
            return {"message": "not_found", "movie": None}

        title = movie_data.get('title')
        director = movie_data.get('director', None)
        rating = movie_data.get('rating', None)
        poster = movie_data.get('poster', None)
        release_year = movie_data.get('release_year', None)

        # Check if the movie already exists in the database
        existing_movie = (
            self.db.session.query(Movie)
            .filter_by(title=title, release_year=release_year)
            .first()
        )
        if not existing_movie:
            # Create a new movie and add it to the database
            new_movie = Movie(
                title=title,
                release_year=release_year,
                director=director,
                rating=rating,
                poster=poster,
            )
            try:
                self.db.session.add(new_movie)
                self.db.session.commit()
                existing_movie = new_movie
            except SQLAlchemyError as error:
                self.db.session.rollback()
                raise ValueError(f"Error occurred while adding movie: {error}")

        # Check if the movie is already linked to the user
        user_movie = (
            self.db.session.query(UserMovies)
            .filter_by(user_id=user_id, movie_id=existing_movie.id)
            .first()
        )
        if user_movie:
            return {"message": "linked", "movie": existing_movie}

        # Link the movie to the user
        user_movie = UserMovies(user_id=user_id, movie_id=existing_movie.id)
        try:
            self.db.session.add(user_movie)
            self.db.session.commit()
        except SQLAlchemyError as error:
            self.db.session.rollback()
            raise ValueError(f"Error occurred while linking movie to user: {error}")

        return {"message": "added", "movie": existing_movie}

    def delete_movie(self, user_id, movie_id):
        try:
            # Find the entry linking the user and movie
            user_movie = self.db.session.query(UserMovies).filter_by(user_id=user_id,
                                                                     movie_id=movie_id).first()
            if not user_movie:
                return None

            movie = self.db.session.query(Movie).filter_by(id=movie_id).first()
            if not movie:
                return None

            # Delete the user and movie relationship
            self.db.session.delete(user_movie)

            # Delete the movie if no other user is associated
            if not self.db.session.query(UserMovies).filter_by(movie_id=movie_id).first():
                self.db.session.delete(movie)

            self.db.session.commit()
            return movie

        except SQLAlchemyError as e:
            print(f"Error deleting movie for user {user_id}: {e}")
            self.db.session.rollback()
            return None

    def update_movie(self, movie_id, user_id, rating=None):
        try:
            movie_to_update = self.get_movie(movie_id)
            if not movie_to_update:
                raise ValueError(f"Movie with ID {movie_id} does not exist.")

            # Update the rating if provided
            movie_to_update.rating = rating or movie_to_update.rating

            self.db.session.commit()

        except SQLAlchemyError as error:
            print(f"Error occurred while updating movie with ID {movie_id}: {error}")
            self.db.session.rollback()
            raise None
