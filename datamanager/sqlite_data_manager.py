from datamanager.data_manager_interface import DataManagerInterface
from datamanager.data_models import User, Movie, UserMovies
from extensions import db
from sqlalchemy.exc import SQLAlchemyError

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
            user = (self.db.session.query(User)
                    .filter(User.id == user_id)
                    .one_or_none())
            if not user:
                raise ValueError(f"No user found with ID {user_id}")
            return user
        except SQLAlchemyError as error:
            print(f"Error fetching user with ID {user_id}: {error}")
            raise  # Re-raise the original exception

