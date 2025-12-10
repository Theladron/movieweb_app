import os
import logging

import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

# Get the API key from environment variables
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

logger = logging.getLogger(__name__)


def fetch_movie_data(title):
    """
    Fetches movie data with the specified title from the OMDb API, handles exceptions
    :param title: title of the movie as string
    :return: movie data as dictionary
    """
    api_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
    except (HTTPError, ConnectionError, Timeout) as req_err:
        logger.warning(f"OMDb API request error for '{title}': {req_err}")
        return None

    try:
        data = response.json()
    except ValueError as json_err:
        logger.error(f"Error parsing OMDb API JSON response for '{title}': {json_err}", exc_info=True)
        return None

    # Catch API error response
    if "Error" in data:
        logger.info(f"OMDb API error for '{title}': {data['Error']}")
        return None

    # Extract relevant movie data
    movie_data = {
        'title': data.get('Title', ''),
        'director': data.get('Director', ''),
        'rating': data.get('imdbRating', ''),
        'release_year': data.get('Year', ''),
        'poster': data.get('Poster', 'N/A')
    }
    return movie_data
