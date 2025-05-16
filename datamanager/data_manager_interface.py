from abc import ABC, abstractmethod

from datamanager.data_models import User, Movie


class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self) -> list[User]:
        """
        Fetches all users from the database
        """
        pass

    @abstractmethod
    def get_all_movies(self) -> list[Movie]:
        """
        Fetches all movies from the database
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id) -> list[Movie]:
        """
        Fetches all movies associated with a user from the database
        """
        pass

    @abstractmethod
    def get_user(self, user_id) -> User:
        """
        Fetches a user by ID from the database
        :param user_id: the id of the user as integer
        """
        pass

    @abstractmethod
    def add_user(self, user: User) -> None:
        """
        Adds a new user to the database
        :param user: the user as User object
        """
        pass

    @abstractmethod
    def update_user(self, user_id, user_name):
        """
        updates the name of a user
        :param user_id: the id of the user as integer
        :param user_name: the name of the user as string
        """
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """
        Deletes a user from the database
        :param user_id: id of the user as integer
        """
        pass

    @abstractmethod
    def get_user_by_name(self, user_name):
        """
        Gets a user by name
        :param user_name: the name of the user as string
        """
        pass

    @abstractmethod
    def add_movie(self, movie: Movie) -> None:
        """
        Adds a movie to the database
        :param movie: the movie as Movie object
        """
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """
        Deletes a movie from the database
        :param movie_id: id of the movie as integer
        """
        pass

    @abstractmethod
    def get_movie(self, movie_id):
        """
        Gets a movie object from the database by ID
        :param movie_id: the id of the movie as integer
        """
        pass

    @abstractmethod
    def update_movie(self, movie_id, user_id, rating=None):
        """
        Updates the rating of a movie
        :param movie_id: id of the movie as integer
        :param user_id: id of the user as integer
        :param rating: new rating of the movie as float
        """
        pass

    @abstractmethod
    def delete_movie(self, user_id, movie_id):
        """
        Deletes a movie from the database
        :param user_id: user id as integer
        :param movie_id: movie id as integer
        :return: the removed movie as Movie object if found, else None
        """
        pass