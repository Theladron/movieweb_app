import os
import logging

import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

# Get the API key from environment variables
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

logger = logging.getLogger(__name__)


def fetch_movie_data(movie_title: str) -> dict | None:
    """Fetch movie data from the OMDb API by title.

    Args:
        movie_title: The title of the movie to search for.

    Returns:
        dict | None: Dictionary containing movie data with keys: title, director,
            rating, release_year, poster. Returns None if movie not found or error occurs.
    """
    omdb_api_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_title}"

    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        http_response = requests.get(omdb_api_url, headers=request_headers)
        http_response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
    except (HTTPError, ConnectionError, Timeout) as request_error:
        logger.warning(f"OMDb API request error for '{movie_title}': {request_error}")
        return None

    try:
        omdb_response_data = http_response.json()
    except ValueError as json_parse_error:
        logger.error(f"Error parsing OMDb API JSON response for '{movie_title}': {json_parse_error}", exc_info=True)
        return None

    # Catch API error response
    if "Error" in omdb_response_data:
        logger.info(f"OMDb API error for '{movie_title}': {omdb_response_data['Error']}")
        return None

    # Extract relevant movie data
    formatted_movie_data = {
        'title': omdb_response_data.get('Title', ''),
        'director': omdb_response_data.get('Director', ''),
        'rating': omdb_response_data.get('imdbRating', ''),
        'release_year': omdb_response_data.get('Year', ''),
        'poster': omdb_response_data.get('Poster', 'N/A')
    }
    return formatted_movie_data
