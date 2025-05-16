from abc import ABC, abstractmethod
from datamanager.data_models import User, Movie

class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self) -> list[User]:
        pass

    @abstractmethod
    def get_all_movies(self) -> list[Movie]:
        pass

    @abstractmethod
    def get_user_movies(self, user_id) -> list[Movie]:
        pass

    @abstractmethod
    def get_user(self, user_id) -> User:
        pass

    @abstractmethod
    def add_user(self, user: User) -> None:
        pass