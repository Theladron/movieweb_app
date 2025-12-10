import logging
from sqlalchemy.exc import SQLAlchemyError

from datamanager.data_manager_interface import DataManagerInterface
from datamanager.data_models import User, Movie, UserMovies
from extensions import db
from services.omdb_api import fetch_movie_data

logger = logging.getLogger(__name__)


class SQLiteDataManager(DataManagerInterface):
    """Data manager implementation for SQLite database operations.

    Provides methods to interact with the database for users, movies,
    and user-movie relationships.

    Attributes:
        db: SQLAlchemy database instance.
        db_path: Path to the database file (set during initialization).
    """

    def __init__(self):
        """Initialize the SQLiteDataManager instance."""
        self.db = db
        self.db_path = None

    def init_app(self, app):
        """Initialize the data manager with the Flask application.

        Args:
            app: The Flask application instance.
        """
        self.db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///movies.db")

    def get_all_users(self) -> list[User]:
        """Fetch all users from the database.

        Returns:
            list[User]: List of all User objects, or empty list if error occurs.
        """
        try:
            return self.db.session.query(User).all()
        except SQLAlchemyError as db_error:
            logger.error(f"Error fetching users: {db_error}", exc_info=True)
            return []

    def get_all_movies(self) -> list[Movie]:
        """Fetch all movies from the database.

        Returns:
            list[Movie]: List of all Movie objects, or empty list if error occurs.
        """
        try:
            return self.db.session.query(Movie).all()
        except SQLAlchemyError as db_error:
            logger.error(f"Error fetching movies: {db_error}", exc_info=True)
            return []

    def get_user_movies(self, user_id: int) -> list[dict]:
        """Fetch all movies associated with a user along with their user ratings.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            list[dict]: List of dictionaries containing movie data and user ratings.
                Each dictionary contains: id, title, release_year, poster, director,
                rating (IMDB), and user_rating (personal). Returns empty list on error.
        """
        try:
            query_results = (
                self.db.session.query(Movie, UserMovies.user_rating)
                .join(UserMovies, UserMovies.movie_id == Movie.id)
                .filter(UserMovies.user_id == user_id)
                .all()
            )
            # Convert to list of dictionaries with movie attributes and user_rating
            movies_list = []
            for movie_obj, user_rating_value in query_results:
                movie_data = {
                    'id': movie_obj.id,
                    'title': movie_obj.title,
                    'release_year': movie_obj.release_year,
                    'poster': movie_obj.poster,
                    'director': movie_obj.director,
                    'rating': movie_obj.rating,  # Keep original IMDB rating
                    'user_rating': user_rating_value  # User's personal rating
                }
                movies_list.append(movie_data)
            return movies_list
        except SQLAlchemyError as db_error:
            logger.error(f"Error fetching user movies for user {user_id}: {db_error}", exc_info=True)
            return []

    def get_user(self, user_id: int) -> User:
        """Fetch a user by ID from the database.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            User: The User object if found.

        Raises:
            ValueError: If user with the given ID is not found.
        """
        try:
            user_obj = self.db.session.query(User).filter(User.id == user_id).one_or_none()
            if not user_obj:
                raise ValueError(f"No user found with ID {user_id}")
            return user_obj
        except SQLAlchemyError as db_error:
            # Re-raise as ValueError for consistency
            raise ValueError(f"No user found with ID {user_id}") from db_error

    def add_user(self, user_name: str) -> str:
        """Add a new user to the database.

        Args:
            user_name: The name of the user to add.

        Returns:
            str: The name of the added user.

        Raises:
            ValueError: If user_name is empty or invalid.
        """
        if not user_name:
            raise ValueError("User name cannot be empty")
        new_user = User(name=user_name)
        self.db.session.add(new_user)
        self.db.session.commit()
        return user_name

    def update_user(self, user_id: int, user_name: str) -> str:
        """Update the name of an existing user.

        Args:
            user_id: The unique identifier of the user to update.
            user_name: The new name for the user.

        Returns:
            str: Success message indicating the user was updated.

        Raises:
            ValueError: If user is not found or update fails.
        """
        try:
            # get_user raises ValueError if user not found
            user_to_update = self.get_user(user_id)
            user_to_update.name = user_name
            self.db.session.commit()
            return f"User '{user_name}' was updated successfully!"

        except SQLAlchemyError as db_error:
            self.db.session.rollback()
            raise ValueError(f"Could not update user with ID {user_id}; {db_error}")

    def delete_user(self, user_id: int) -> str:
        """Delete a user from the database.

        Also deletes associated user-movie links and removes movies that
        are no longer associated with any users.

        Args:
            user_id: The unique identifier of the user to delete.

        Returns:
            str: The name of the deleted user.

        Raises:
            ValueError: If user is not found or deletion fails.
        """
        try:
            user_to_delete = self.get_user(user_id)
            if not user_to_delete:
                raise ValueError(f"No user found with ID {user_id}")

            # Get all movie IDs associated with the user
            user_movie_links = self.db.session.query(UserMovies).filter_by(user_id=user_id).all()
            associated_movie_ids = [user_movie.movie_id for user_movie in user_movie_links]

            # Delete the user's entries in UserMovies
            self.db.session.query(UserMovies).filter_by(user_id=user_id).delete()

            # Delete the user
            deleted_user_name = user_to_delete.name
            self.db.session.delete(user_to_delete)
            self.db.session.commit()

            # Delete movies that are no longer associated with any users
            for movie_id in associated_movie_ids:
                remaining_links = self.db.session.query(UserMovies).filter_by(movie_id=movie_id).first()
                if not remaining_links:
                    self.db.session.query(Movie).filter_by(id=movie_id).delete()

            self.db.session.commit()

            return deleted_user_name

        except SQLAlchemyError as db_error:
            self.db.session.rollback()
            raise ValueError(f"Error occurred while deleting user with ID {user_id}: {db_error}")

    def get_user_by_name(self, user_name: str) -> User:
        """Get a user by their name.

        Args:
            user_name: The name of the user to search for.

        Returns:
            User: The User object if found, None otherwise.

        Raises:
            SQLAlchemyError: If a database error occurs.
        """
        try:
            user_obj = self.db.session.query(User).filter(User.name == user_name).one_or_none()
            return user_obj
        except SQLAlchemyError as db_error:
            raise SQLAlchemyError(f"Error fetching user by name: {db_error}") from db_error

    def get_movie(self, movie_id: int) -> Movie:
        """Get a movie object from the database by ID.

        Args:
            movie_id: The unique identifier of the movie.

        Returns:
            Movie: The Movie object if found.

        Raises:
            ValueError: If movie with the given ID is not found.
        """
        try:
            movie_obj = self.db.session.query(Movie).filter(Movie.id == movie_id).one_or_none()
            if not movie_obj:
                raise ValueError(f"No movie found with ID {movie_id}")
            return movie_obj
        except SQLAlchemyError as db_error:
            # Re-raise as ValueError for consistency
            raise ValueError(f"No movie found with ID {movie_id}") from db_error

    def get_user_movie_rating(self, user_id: int, movie_id: int) -> float | None:
        """Get a user's rating for a specific movie.

        Args:
            user_id: The unique identifier of the user.
            movie_id: The unique identifier of the movie.

        Returns:
            float: The user's rating for the movie, or None if not found.

        Raises:
            SQLAlchemyError: If a database error occurs.
        """
        try:
            user_movie_link = (
                self.db.session.query(UserMovies)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )
            return user_movie_link.user_rating if user_movie_link else None
        except SQLAlchemyError as db_error:
            raise SQLAlchemyError(f"Error fetching user movie rating: {db_error}") from db_error

    def add_movie(self, user_id: int, title: str) -> dict:
        """Add a movie to a user's collection.

        Fetches movie data from OMDb API and creates the movie if it doesn't exist.
        Links the movie to the user with an initial rating.

        Args:
            user_id: The unique identifier of the user.
            title: The title of the movie to add.

        Returns:
            dict: Dictionary with 'message' key ('added', 'linked', 'not_found') and 'movie' key.

        Raises:
            ValueError: If movie cannot be added due to validation or database errors.
        """
        # Fetch movie data from OMDb API
        omdb_movie_data = fetch_movie_data(title)
        if not omdb_movie_data:
            return {"message": "not_found", "movie": None}

        # Extract movie information from API response
        movie_title_from_api = omdb_movie_data.get('title')
        movie_director = omdb_movie_data.get('director', None)
        imdb_rating_value = omdb_movie_data.get('rating', None)
        movie_poster_url = omdb_movie_data.get('poster', None)
        movie_release_year = omdb_movie_data.get('release_year', None)

        # Check if the movie already exists in the database
        existing_movie = (
            self.db.session.query(Movie)
            .filter_by(title=movie_title_from_api, release_year=movie_release_year)
            .first()
        )
        if not existing_movie:
            # Create a new movie and add it to the database
            new_movie = Movie(
                title=movie_title_from_api,
                release_year=movie_release_year,
                director=movie_director,
                rating=imdb_rating_value,
                poster=movie_poster_url,
            )
            try:
                self.db.session.add(new_movie)
                self.db.session.commit()
                existing_movie = new_movie
            except SQLAlchemyError as db_error:
                self.db.session.rollback()
                raise ValueError(f"Error occurred while adding movie: {db_error}")

        # Check if the movie is already linked to the user
        existing_user_movie_link = (
            self.db.session.query(UserMovies)
            .filter_by(user_id=user_id, movie_id=existing_movie.id)
            .first()
        )
        if existing_user_movie_link:
            return {"message": "linked", "movie": existing_movie}

        # Link the movie to the user with initial rating from the movie
        # Convert rating to float if it's a string
        initial_user_rating = imdb_rating_value
        if isinstance(imdb_rating_value, str):
            try:
                initial_user_rating = float(imdb_rating_value) if imdb_rating_value else None
            except (ValueError, TypeError):
                initial_user_rating = None
        
        user_movie_link = UserMovies(
            user_id=user_id, 
            movie_id=existing_movie.id,
            user_rating=initial_user_rating
        )
        try:
            self.db.session.add(user_movie_link)
            self.db.session.commit()
        except SQLAlchemyError as db_error:
            self.db.session.rollback()
            raise ValueError(f"Error occurred while linking movie to user: {db_error}")

        return {"message": "added", "movie": existing_movie}

    def delete_movie(self, user_id: int, movie_id: int) -> Movie:
        """Delete a movie from a user's collection.

        If no other users have the movie, deletes it from the database entirely.

        Args:
            user_id: The unique identifier of the user.
            movie_id: The unique identifier of the movie to remove.

        Returns:
            Movie: The deleted Movie object if found, None otherwise.
        """
        try:
            # Find the entry linking the user and movie
            user_movie_link = (
                self.db.session.query(UserMovies)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )
            if not user_movie_link:
                return None

            movie_obj = self.db.session.query(Movie).filter_by(id=movie_id).first()
            if not movie_obj:
                return None

            # Check if any other users have this movie before deleting the link
            other_users_count = (
                self.db.session.query(UserMovies)
                .filter_by(movie_id=movie_id)
                .filter(UserMovies.user_id != user_id)
                .count()
            )

            # Delete the user and movie relationship
            self.db.session.delete(user_movie_link)

            # Delete the movie if no other user is associated
            if other_users_count == 0:
                self.db.session.delete(movie_obj)

            self.db.session.commit()
            return movie_obj

        except SQLAlchemyError as db_error:
            logger.error(f"Error deleting movie {movie_id} for user {user_id}: {db_error}", exc_info=True)
            self.db.session.rollback()
            return None

    def update_movie(self, movie_id: int, user_id: int, rating: float = None) -> None:
        """Update a user's rating for a movie in the linking table.

        Args:
            movie_id: The unique identifier of the movie.
            user_id: The unique identifier of the user.
            rating: The new user rating for the movie (optional).

        Raises:
            ValueError: If user-movie link is not found or update fails.
        """
        try:
            # Find the linking entry for this user and movie first
            user_movie_link = (
                self.db.session.query(UserMovies)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if not user_movie_link:
                raise ValueError(f"User has not added movie with ID {movie_id}.")

            # Update the user's rating in the linking table
            if rating is not None:
                user_movie_link.user_rating = rating

            self.db.session.commit()

        except SQLAlchemyError as db_error:
            logger.error(f"Error occurred while updating movie rating for user {user_id}: {db_error}", exc_info=True)
            self.db.session.rollback()
            raise ValueError(f"Error occurred while updating movie rating: {db_error}")
