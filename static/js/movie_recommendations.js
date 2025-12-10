/**
 * JavaScript for movie recommendations feature
 * Handles API calls and dynamic display of recommendations
 */

/**
 * Fetch movie recommendations from the API
 * @param {string} movieTitle - The title of the movie to get recommendations for
 * @returns {Promise<Object>} - Promise resolving to recommendations data or error
 */
async function fetchRecommendations(movieTitle) {
    try {
        const response = await fetch(`/api/movies/recommendations?title=${encodeURIComponent(movieTitle)}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch recommendations');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        throw error;
    }
}

/**
 * Display recommendations in the recommendations container
 * @param {string} originalMovie - The original movie title
 * @param {Array<string>} recommendations - Array of recommended movie titles
 */
function displayRecommendations(originalMovie, recommendations) {
    const container = document.getElementById('recommendations_container');
    
    if (!container) {
        console.error('Recommendations container not found');
        return;
    }
    
    // Create recommendations card
    const card = document.createElement('div');
    card.className = 'recommendations_card';
    
    // Create title
    const title = document.createElement('h3');
    title.className = 'recommendations_title';
    title.textContent = `Movies similar to "${originalMovie}":`;
    card.appendChild(title);
    
    // Create list of recommendations
    const list = document.createElement('div');
    list.className = 'recommendations_list';
    
    recommendations.forEach((movie) => {
        const item = document.createElement('span');
        item.className = 'recommendation_item';
        item.textContent = movie;
        
        list.appendChild(item);
    });
    
    card.appendChild(list);
    
    // Create close button
    const closeButton = document.createElement('button');
    closeButton.className = 'recommendations_close';
    closeButton.innerHTML = '×';
    closeButton.setAttribute('aria-label', 'Close recommendations');
    closeButton.onclick = () => {
        container.innerHTML = '';
    };
    card.appendChild(closeButton);
    
    // Clear container and add new card
    container.innerHTML = '';
    container.appendChild(card);
    
    // Scroll to recommendations (smooth scroll)
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Show error message in recommendations container
 * @param {string} errorMessage - Error message to display
 */
function showRecommendationsError(errorMessage) {
    const container = document.getElementById('recommendations_container');
    
    if (!container) {
        console.error('Recommendations container not found');
        return;
    }
    
    const card = document.createElement('div');
    card.className = 'recommendations_card recommendations_error';
    
    const message = document.createElement('p');
    message.className = 'recommendations_message';
    message.textContent = `Error: ${errorMessage}`;
    card.appendChild(message);
    
    const closeButton = document.createElement('button');
    closeButton.className = 'recommendations_close';
    closeButton.innerHTML = '×';
    closeButton.setAttribute('aria-label', 'Close error message');
    closeButton.onclick = () => {
        container.innerHTML = '';
    };
    card.appendChild(closeButton);
    
    container.innerHTML = '';
    container.appendChild(card);
}

/**
 * Show loading state
 */
function showRecommendationsLoading() {
    const container = document.getElementById('recommendations_container');
    
    if (!container) {
        console.error('Recommendations container not found');
        return;
    }
    
    const card = document.createElement('div');
    card.className = 'recommendations_card recommendations_loading';
    
    const message = document.createElement('p');
    message.className = 'recommendations_message';
    message.textContent = 'Loading recommendations...';
    card.appendChild(message);
    
    container.innerHTML = '';
    container.appendChild(card);
}

/**
 * Handle recommendation button click
 * @param {string} movieTitle - The title of the movie to get recommendations for
 */
async function handleRecommendationsClick(movieTitle) {
    const container = document.getElementById('recommendations_container');
    
    if (!container) {
        console.error('Recommendations container not found');
        return;
    }
    
    // Show loading state
    showRecommendationsLoading();
    
    try {
        // Fetch recommendations
        const data = await fetchRecommendations(movieTitle);
        
        if (data.success && data.recommendations && data.recommendations.length > 0) {
            // Display recommendations
            displayRecommendations(data.original_movie, data.recommendations);
        } else {
            showRecommendationsError('No recommendations found for this movie.');
        }
    } catch (error) {
        showRecommendationsError(error.message || 'Failed to load recommendations. Please try again.');
    }
}

