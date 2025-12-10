import os
import logging
import json
import re

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

# Get the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logger = logging.getLogger(__name__)

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def get_similar_movies(movie_title):
    """
    Get AI-powered movie recommendations based on a movie title.
    
    :param movie_title: Title of the movie to find similar movies for
    :return: List of recommended movie titles, or None if error occurred
    """
    if not GEMINI_AVAILABLE:
        logger.error("google-generativeai package not installed")
        return None
    
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set in environment variables. Please check your .env file and docker-compose.yml")
        return None
    
    if not movie_title or not movie_title.strip():
        logger.warning("Empty movie title provided")
        return None
    
    try:
        # Create prompt for Gemini
        prompt = f"""Based on the movie "{movie_title}", suggest 5 similar movies that a viewer would likely enjoy.

Please respond with ONLY a JSON array of movie titles, nothing else. Format: ["Movie Title 1", "Movie Title 2", "Movie Title 3", "Movie Title 4", "Movie Title 5"]

Focus on movies that are similar in:
- Genre
- Tone
- Themes
- Style
- Target audience

Return the movies as a JSON array only."""

        # Use Gemini model - gemini-flash-latest is free tier compatible
        # gemini-2.0-flash has limit 0 for free tier, so we use the "latest" variant
        # Available models can be checked with: genai.list_models()
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        
        # Extract text from response
        response_text = response.text.strip()
        
        # Try to parse as JSON first
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_text = response_text
            if '```json' in cleaned_text:
                cleaned_text = cleaned_text.split('```json')[1].split('```')[0].strip()
            elif '```' in cleaned_text:
                cleaned_text = cleaned_text.split('```')[1].split('```')[0].strip()
            
            movies = json.loads(cleaned_text)
            if isinstance(movies, list) and len(movies) > 0:
                logger.info(f"Successfully got {len(movies)} recommendations for '{movie_title}'")
                return movies
            else:
                logger.warning(f"Empty or invalid movie list returned for '{movie_title}'")
                return None
                
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract movie titles from text
            logger.warning(f"Failed to parse JSON response for '{movie_title}', attempting text extraction")
            movies = _extract_movies_from_text(response_text)
            if movies:
                logger.info(f"Successfully extracted {len(movies)} recommendations from text for '{movie_title}'")
                return movies
            else:
                logger.error(f"Could not extract movie titles from response for '{movie_title}'")
                return None
            
    except Exception as error:
        error_str = str(error)
        # Check for quota/rate limit errors
        if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
            logger.warning(f"Quota/rate limit exceeded for '{movie_title}': {error_str[:200]}")
            # Try to extract retry delay if available
            if "retry in" in error_str.lower():
                logger.info("Please wait before retrying the request.")
        else:
            logger.error(f"Error getting movie recommendations for '{movie_title}': {error}", exc_info=True)
        return None


def _extract_movies_from_text(text):
    """
    Fallback method to extract movie titles from text response.
    Tries to find quoted strings or numbered list items.
    
    :param text: Text response from AI
    :return: List of movie titles or None
    """
    movies = []
    
    # Try to find quoted strings (common in AI responses)
    quoted_pattern = r'"([^"]+)"'
    quoted_matches = re.findall(quoted_pattern, text)
    if quoted_matches:
        movies.extend(quoted_matches)
    
    # Try to find numbered list items (1. Movie Title)
    numbered_pattern = r'\d+\.\s*([^\n]+)'
    numbered_matches = re.findall(numbered_pattern, text)
    if numbered_matches:
        # Only add if we didn't find quoted strings, or if we need more movies
        if not movies or len(movies) < 3:
            movies.extend([m.strip() for m in numbered_matches[:5]])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_movies = []
    for movie in movies:
        movie_clean = movie.strip().strip('"').strip("'")
        if movie_clean and movie_clean.lower() not in seen:
            seen.add(movie_clean.lower())
            unique_movies.append(movie_clean)
    
    return unique_movies[:5] if unique_movies else None

