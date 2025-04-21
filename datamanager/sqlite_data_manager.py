from flask_sqlalchemy import SQLAlchemy
from datamanager.data_manager_interface import DataManagerInterface
from datamanager.data_models import User, Movie, UserMovies, db


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        db.init_app(app)
        self.db = db

    def get_all_users(self):
        pass

    def get_user_movies(self, user_id):
        pass