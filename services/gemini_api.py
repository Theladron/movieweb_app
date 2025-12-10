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


def get_similar_movies(movie_title: str) -> list[str] | None:
    """Get AI-powered movie recommendations based on a movie title.

    Uses Google Gemini API to generate similar movie recommendations.

    Args:
        movie_title: The title of the movie to find similar movies for.

    Returns:
        list[str] | None: List of recommended movie titles, or None if error occurred.
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

        # Extract text from response, handling multi-part content
        try:
            response_text = response.text.strip()
        except Exception:
            # Fallback: concatenate any text parts
            response_parts = []
            for candidate in getattr(response, "candidates", []) or []:
                for part in getattr(getattr(candidate, "content", None), "parts", []) or []:
                    text_part = getattr(part, "text", None)
                    if text_part:
                        response_parts.append(text_part)
            response_text = "\n".join(response_parts).strip()
        
        # Try to parse as JSON first
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response_text = response_text
            if '```json' in cleaned_response_text:
                cleaned_response_text = cleaned_response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in cleaned_response_text:
                cleaned_response_text = cleaned_response_text.split('```')[1].split('```')[0].strip()
            
            recommendations_list = json.loads(cleaned_response_text)
            if isinstance(recommendations_list, list) and len(recommendations_list) > 0:
                logger.info(f"Successfully got {len(recommendations_list)} recommendations for '{movie_title}'")
                return recommendations_list
            else:
                logger.warning(f"Empty or invalid movie list returned for '{movie_title}'")
                return None
                
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract movie titles from text
            logger.warning(f"Failed to parse JSON response for '{movie_title}', attempting text extraction")
            extracted_movies = _extract_movies_from_text(response_text)
            if extracted_movies:
                logger.info(f"Successfully extracted {len(extracted_movies)} recommendations from text for '{movie_title}'")
                return extracted_movies
            else:
                logger.error(f"Could not extract movie titles from response for '{movie_title}'")
                return None
            
    except Exception as api_error:
        error_message = str(api_error)
        # Check for quota/rate limit errors
        if "429" in error_message or "quota" in error_message.lower() or "ResourceExhausted" in error_message:
            logger.warning(f"Quota/rate limit exceeded for '{movie_title}': {error_message[:200]}")
            # Try to extract retry delay if available
            if "retry in" in error_message.lower():
                logger.info("Please wait before retrying the request.")
        else:
            logger.error(f"Error getting movie recommendations for '{movie_title}': {api_error}", exc_info=True)
        return None


def _extract_movies_from_text(text: str) -> list[str] | None:
    """Extract movie titles from text response (fallback method).

    Tries to find quoted strings or numbered list items when JSON parsing fails.

    Args:
        text: Raw text response from the AI API.

    Returns:
        list[str]: List of extracted movie titles (up to 5), or None if none found.
    """
    extracted_titles = []
    
    # Try to find quoted strings (common in AI responses)
    quoted_pattern = r'"([^"]+)"'
    quoted_matches = re.findall(quoted_pattern, text)
    if quoted_matches:
        extracted_titles.extend(quoted_matches)
    
    # Try to find numbered list items (1. Movie Title)
    numbered_pattern = r'\d+\.\s*([^\n]+)'
    numbered_matches = re.findall(numbered_pattern, text)
    if numbered_matches:
        # Only add if we didn't find quoted strings, or if we need more movies
        if not extracted_titles or len(extracted_titles) < 3:
            extracted_titles.extend([match.strip() for match in numbered_matches[:5]])
    
    # Remove duplicates while preserving order
    seen_titles = set()
    unique_titles = []
    for title in extracted_titles:
        cleaned_title = title.strip().strip('"').strip("'")
        if cleaned_title and cleaned_title.lower() not in seen_titles:
            seen_titles.add(cleaned_title.lower())
            unique_titles.append(cleaned_title)
    
    return unique_titles[:5] if unique_titles else None

