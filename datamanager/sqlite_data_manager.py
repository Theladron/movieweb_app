from sqlalchemy.exc import SQLAlchemyError

from datamanager.data_manager_interface import DataManagerInterface
from datamanager.data_models import User, Movie, UserMovies
from extensions import db
from services.omdb_api import fetch_movie_data


class SQLiteDataManager(DataManagerInterface):
    """
    Imitates a data manager for a SQLite database.

    Attributes:
        db (SQLAlchemy): SQLAlchemy instance
        db_path (str): Path to the database file
        """

    def __init__(self):
        """Initializes the SQLiteDataManager instance."""
        self.db = db
        self.db_path = None

    def init_app(self, app):
        """Initializes the SQLiteDataManager instance with the provided Flask app."""
        self.db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///movies.db")

    def get_all_users(self):
        """
        Fetches all users from the database
        :return: All users as a list if found, else an empty list
        """
        try:
            return self.db.session.query(User).all()
        except SQLAlchemyError as error:
            print(f"Error fetching users: {error}")
            return []

    def get_all_movies(self):
        """
        Fetches all movies from the database
        :return: all movies as a list if found, else an empty list
        """
        try:
            return self.db.session.query(Movie).all()
        except SQLAlchemyError as error:
            print(f"Error fetching movies: {error}")
            return []

    def get_user_movies(self, user_id):
        """
        Fetches all movies associated with a user from the database along with user_rating
        :return: all movies with user_rating as a list of dictionaries if found, else an empty list
        """
        try:
            results = (
                self.db.session.query(Movie, UserMovies.user_rating)
                .join(UserMovies, UserMovies.movie_id == Movie.id)
                .filter(UserMovies.user_id == user_id)
                .all()
            )
            # Convert to list of dictionaries with movie attributes and user_rating
            movies = []
            for movie, user_rating in results:
                movie_dict = {
                    'id': movie.id,
                    'title': movie.title,
                    'release_year': movie.release_year,
                    'poster': movie.poster,
                    'director': movie.director,
                    'rating': movie.rating,  # Keep original IMDB rating
                    'user_rating': user_rating  # User's personal rating
                }
                movies.append(movie_dict)
            return movies
        except SQLAlchemyError as error:
            print(f"Error fetching user movies: {error}")
            return []

    def get_user(self, user_id):
        """
        Fetches a user by ID from the database
        :return: User object if found, else None
        """
        try:
            user = (self.db.session.query(User).filter(User.id == user_id).one_or_none())
            if not user:
                raise ValueError(f"No user found with ID {user_id}")
            return user
        except SQLAlchemyError as error:
            print(f"Error fetching user with ID {user_id}: {error}")
            return

    def add_user(self, user_name):
        """
        Adds a new user to the database
        :param user_name: name of the user as string
        :return: name of the user as string
        """
        if not user_name:
            raise ValueError("User name cannot be empty")
        new_user = User(name=user_name)
        self.db.session.add(new_user)
        self.db.session.commit()
        return user_name

    def update_user(self, user_id, user_name):
        """
        updates the name of a user
        :param user_id: the id of the user as integer
        :param user_name: the name of the user as string
        :return: the updated name of the user if found, else an error message as string
        """
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
        """
        Deletes a user from the database
        :param user_id: id of the user as integer
        :return: name of the deleted user as string if found, else None
        """
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
        """
        Gets a user by name
        :param user_name: the name of the user as string
        :return: user as User object
        """
        try:
            user = self.db.session.query(User).filter(User.name == user_name).one_or_none()
            return user
        except SQLAlchemyError as error:
            raise SQLAlchemyError(f"Error fetching user by name: {error}")

    def get_movie(self, movie_id):
        """
        Gets a movie object from the database by ID
        :param movie_id: the id of the movie as integer
        :return: movie as Movie object
        """
        try:
            movie = self.db.session.query(Movie).filter(Movie.id == movie_id).one_or_none()
            if not movie:
                raise ValueError(f"No movie found with ID {movie_id}")
            return movie
        except SQLAlchemyError as error:
            raise SQLAlchemyError(f"Error fetching movie with ID {movie_id}: {error}")

    def get_user_movie_rating(self, user_id, movie_id):
        """
        Gets the user's rating for a specific movie
        :param user_id: the id of the user as integer
        :param movie_id: the id of the movie as integer
        :return: user_rating as float or None if not found
        """
        try:
            user_movie = (
                self.db.session.query(UserMovies)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )
            return user_movie.user_rating if user_movie else None
        except SQLAlchemyError as error:
            raise SQLAlchemyError(f"Error fetching user movie rating: {error}")

    def add_movie(self, user_id, title):
        """
        Adds a movie to the database
        :param user_id: id of the user as integer
        :param title: title of the movie as string
        :return: status codes as dictionary
        """
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

        # Link the movie to the user with initial rating from the movie
        # Convert rating to float if it's a string
        initial_rating = rating
        if isinstance(rating, str):
            try:
                initial_rating = float(rating) if rating else None
            except (ValueError, TypeError):
                initial_rating = None
        
        user_movie = UserMovies(
            user_id=user_id, 
            movie_id=existing_movie.id,
            user_rating=initial_rating
        )
        try:
            self.db.session.add(user_movie)
            self.db.session.commit()
        except SQLAlchemyError as error:
            self.db.session.rollback()
            raise ValueError(f"Error occurred while linking movie to user: {error}")

        return {"message": "added", "movie": existing_movie}

    def delete_movie(self, user_id, movie_id):
        """
        Deletes a movie from the user's list. If no other users have the movie,
        deletes the movie from the database entirely.
        :param user_id: user id as integer
        :param movie_id: movie id as integer
        :return: the removed movie as Movie object if found, else None
        """
        try:
            # Find the entry linking the user and movie
            user_movie = self.db.session.query(UserMovies).filter_by(user_id=user_id,
                                                                     movie_id=movie_id).first()
            if not user_movie:
                return None

            movie = self.db.session.query(Movie).filter_by(id=movie_id).first()
            if not movie:
                return None

            # Check if any other users have this movie before deleting the link
            other_links_count = (
                self.db.session.query(UserMovies)
                .filter_by(movie_id=movie_id)
                .filter(UserMovies.user_id != user_id)
                .count()
            )

            # Delete the user and movie relationship
            self.db.session.delete(user_movie)

            # Delete the movie if no other user is associated
            if other_links_count == 0:
                self.db.session.delete(movie)

            self.db.session.commit()
            return movie

        except SQLAlchemyError as e:
            print(f"Error deleting movie for user {user_id}: {e}")
            self.db.session.rollback()
            return None

    def update_movie(self, movie_id, user_id, rating=None):
        """
        Updates the user's rating for a movie in the linking table
        :param movie_id: id of the movie as integer
        :param user_id: id of the user as integer
        :param rating: new user rating for the movie as float
        """
        try:
            # Verify the movie exists
            movie_to_update = self.get_movie(movie_id)
            if not movie_to_update:
                raise ValueError(f"Movie with ID {movie_id} does not exist.")

            # Find the linking entry for this user and movie
            user_movie = (
                self.db.session.query(UserMovies)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )
            
            if not user_movie:
                raise ValueError(f"Movie with ID {movie_id} is not linked to user with ID {user_id}.")

            # Update the user's rating in the linking table
            if rating is not None:
                user_movie.user_rating = rating

            self.db.session.commit()

        except SQLAlchemyError as error:
            print(f"Error occurred while updating movie rating for user {user_id}: {error}")
            self.db.session.rollback()
            raise ValueError(f"Error occurred while updating movie rating: {error}")
