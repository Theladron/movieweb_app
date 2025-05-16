from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    Represents a user in the database.

    Attributes:
        id (int): The unique identifier for the user.
        name (str): The name of the user.
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    user_movies = db.relationship('UserMovies', back_populates='user', cascade='all, delete')

    def __repr__(self):
        return f'User(id = {self.id}, name = {self.name})'

    def __str__(self):
        return f"{self.id}, {self.name}"


class Movie(db.Model):
    """Represents a movie in the database.

    Attributes:
        id (int): The unique identifier for the movie.
        title (str): The title of the movie.
        release_year (int): The release year of the movie.
        poster (str): The URL of the movie poster.
        director (str): The director of the movie.
        rating (float): The rating of the movie."""
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    release_year = db.Column(db.Integer, nullable=True)
    poster = db.Column(db.String, nullable=True)
    director = db.Column(db.String, nullable=True)
    rating = db.Column(db.Float, nullable=False)

    user_movies = db.relationship('UserMovies', back_populates='movie', cascade='all, delete')

    def __repr__(self):
        return (f'Movie(id = {self.id}, title = {self.title}, release_year = {self.release_year}, '
                f'poster = {self.poster}, director = {self.director}, rating = {self.rating})')

    def __str__(self):
        return f"{self.id}, {self.title}, {self.release_year}"


class UserMovies(db.Model):
    """The connection table between users and movies.

    Attributes:
        id (int): The unique identifier for the connection.
        user_id(int): The id of the user.
        movie_id (int): The id of the movie."""
    __tablename__ = 'user_movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    user = db.relationship('User', back_populates='user_movies')
    movie = db.relationship('Movie', back_populates='user_movies')

    def __repr__(self):
        return f'UserMovies(id = {self.id}, user_id = {self.user_id}, movie_id = {self.movie_id})'
