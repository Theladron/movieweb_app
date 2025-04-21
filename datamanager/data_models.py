from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    user_movies = db.relationship('UserMovies', back_populates='user', cascade='all, delete')

    def __repr__(self):
        return f'User(id = {self.id}, name = {self.name})'

    def __str__(self):
        return f"{self.id}, {self.name}"

class Movie(db.Model):

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

    __tablename__ = 'user_movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    user = db.relationship('User', back_populates='user_movies')
    movie = db.relationship('Movie', back_populates='user_movies')

    def __repr__(self):
        return f'UserMovies(id = {self.id}, user_id = {self.user_id}, movie_id = {self.movie_id})'
