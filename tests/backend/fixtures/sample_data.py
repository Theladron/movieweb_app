"""
Sample data fixtures for testing.
"""
from datamanager.data_models import User, Movie, UserMovies


# Sample user data
SAMPLE_USERS = [
    {"name": "Alice"},
    {"name": "Bob"},
    {"name": "Charlie"},
]

# Sample movie data
SAMPLE_MOVIES = [
    {
        "title": "The Matrix",
        "release_year": 1999,
        "director": "Lana Wachowski, Lilly Wachowski",
        "rating": 8.7,
        "poster": "https://example.com/matrix.jpg"
    },
    {
        "title": "Inception",
        "release_year": 2010,
        "director": "Christopher Nolan",
        "rating": 8.8,
        "poster": "https://example.com/inception.jpg"
    },
    {
        "title": "Interstellar",
        "release_year": 2014,
        "director": "Christopher Nolan",
        "rating": 8.6,
        "poster": "https://example.com/interstellar.jpg"
    },
]

# Sample OMDb API responses
SAMPLE_OMDB_RESPONSE = {
    "Title": "The Matrix",
    "Year": "1999",
    "Director": "Lana Wachowski, Lilly Wachowski",
    "imdbRating": "8.7",
    "Poster": "https://example.com/matrix.jpg"
}

SAMPLE_OMDB_RESPONSE_NOT_FOUND = {
    "Response": "False",
    "Error": "Movie not found!"
}

