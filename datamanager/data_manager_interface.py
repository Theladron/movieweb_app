from abc import ABC, abstractmethod

from datamanager.data_models import User, Movie


class DataManagerInterface(ABC):
    """Abstract interface for data management operations."""

    @abstractmethod
    def get_all_users(self) -> list[User]:
        """Fetch all users from the database.

        Returns:
            list[User]: List of all User objects in the database.
        """
        pass

    @abstractmethod
    def get_all_movies(self) -> list[Movie]:
        """Fetch all movies from the database.

        Returns:
            list[Movie]: List of all Movie objects in the database.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id: int) -> list[dict]:
        """Fetch all movies associated with a user from the database.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            list[dict]: List of dictionaries containing movie data and user ratings.
        """
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        """Fetch a user by ID from the database.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            User: The User object if found.

        Raises:
            ValueError: If user with the given ID is not found.
        """
        pass

    @abstractmethod
    def add_user(self, user_name: str) -> str:
        """Add a new user to the database.

        Args:
            user_name: The name of the user to add.

        Returns:
            str: The name of the added user.

        Raises:
            ValueError: If user_name is empty or invalid.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> str:
        """Delete a user from the database.

        Args:
            user_id: The unique identifier of the user to delete.

        Returns:
            str: The name of the deleted user.

        Raises:
            ValueError: If user is not found or deletion fails.
        """
        pass

    @abstractmethod
    def get_user_by_name(self, user_name: str) -> User:
        """Get a user by their name.

        Args:
            user_name: The name of the user to search for.

        Returns:
            User: The User object if found, None otherwise.

        Raises:
            SQLAlchemyError: If a database error occurs.
        """
        pass

    @abstractmethod
    def add_movie(self, user_id: int, title: str) -> dict:
        """Add a movie to a user's collection.

        Args:
            user_id: The unique identifier of the user.
            title: The title of the movie to add.

        Returns:
            dict: Dictionary with 'message' key indicating status and 'movie' key with Movie object.
                Message values: 'added', 'linked', 'not_found'.

        Raises:
            ValueError: If movie cannot be added due to validation or database errors.
        """
        pass

    @abstractmethod
    def get_movie(self, movie_id: int) -> Movie:
        """Get a movie object from the database by ID.

        Args:
            movie_id: The unique identifier of the movie.

        Returns:
            Movie: The Movie object if found.

        Raises:
            ValueError: If movie with the given ID is not found.
        """
        pass

    @abstractmethod
    def update_movie(self, movie_id: int, user_id: int, rating: float = None) -> None:
        """Update a user's rating for a movie in the linking table.

        Args:
            movie_id: The unique identifier of the movie.
            user_id: The unique identifier of the user.
            rating: The new user rating for the movie (optional).

        Raises:
            ValueError: If user-movie link is not found or update fails.
        """
        pass

    @abstractmethod
    def delete_movie(self, user_id: int, movie_id: int) -> Movie:
        """Delete a movie from a user's collection.

        If no other users have the movie, deletes it from the database entirely.

        Args:
            user_id: The unique identifier of the user.
            movie_id: The unique identifier of the movie to remove.

        Returns:
            Movie: The deleted Movie object if found, None otherwise.
        """
        pass