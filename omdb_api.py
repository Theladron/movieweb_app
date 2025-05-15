import os
import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, ConnectionError, Timeout

# Load environment variables from a .env file
load_dotenv()

# Get the API key from environment variables
API_KEY = os.getenv("API_KEY")


def fetch_movie_data(title):
    api_url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
    except (HTTPError, ConnectionError, Timeout) as req_err:
        print(f"Request error occurred: {req_err}")
        return None

    try:
        data = response.json()
    except ValueError as json_err:
        print(f"Error parsing JSON: {json_err}")
        return None

    # Catch API error response
    if "Error" in data:
        print(f"Error fetching movie data: {data['Error']}")
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
