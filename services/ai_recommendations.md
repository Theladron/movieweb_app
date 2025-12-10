# AI Movie Recommendations Implementation Guide

## Recommended API: Google Gemini API

**Free Tier:** 60 requests per minute (15 RPM for certain models)  
**Best for:** Natural language processing, contextual recommendations, analyzing user ratings

## Setup Instructions

### 1. Get API Key
- Visit: https://ai.google.dev/
- Sign up with Google account
- Create a new API key
- Add to `.env` file: `GEMINI_API_KEY=your_key_here`

### 2. Install Dependency
```bash
pip install google-generativeai
```

### 3. Implementation Ideas

#### Option A: Recommendations Based on User's Rated Movies
Analyze user's existing movie ratings to suggest similar films.

#### Option B: Natural Language Queries
Allow users to input requests like:
- "I want a thrilling action movie"
- "Something similar to The Matrix"
- "A comedy from the 90s"

#### Option C: Hybrid Approach
Combine user's rating history with natural language preferences.

## Example Integration

```python
# services/gemini_api.py (to be created)
import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_movie_recommendations(user_movies, user_query=None):
    """
    Get AI-powered movie recommendations.
    
    Args:
        user_movies: List of movies user has rated (from database)
        user_query: Optional natural language query
        
    Returns:
        List of recommended movie titles
    """
    # Build context from user's movie history
    context = f"User has rated these movies: {user_movies}"
    
    if user_query:
        prompt = f"{context}\n\nUser wants: {user_query}\n\nSuggest 5 similar movies."
    else:
        prompt = f"{context}\n\nSuggest 5 movies the user might like based on their ratings."
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    # Parse response to extract movie titles
    # Return list of movie titles
    return parse_recommendations(response.text)
```

## Alternative: Groq API

If you prefer Groq (faster inference):
- Visit: https://groq.com/
- Free tier: Very generous limits
- Install: `pip install groq`
- Similar implementation pattern

## Next Steps

1. Choose API (Gemini recommended)
2. Create `services/gemini_api.py` or `services/groq_api.py`
3. Add route in `routes/movie.py` for recommendations
4. Create UI component for displaying recommendations
5. Add recommendation button/feature to user movies page

