/**
 * API service layer for the LegalTech frontend.
 * 
 * Single point of contact with the backend.
 * Easy to swap base URL or add auth headers in the future.
 */

const API_BASE_URL = 'http://localhost:8000/api';
const REQUEST_TIMEOUT = 75000; // 75 seconds (DataJud is slow)

/**
 * Search for jurisprudência by query term.
 * 
 * @param {string} query - Search term
 * @returns {Promise<{results: Array, query: string, total: number, error?: string}>}
 */
export async function searchJurisprudencia(query) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const url = `${API_BASE_URL}/search?q=${encodeURIComponent(query)}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      signal: controller.signal,
    });

    const data = await response.json();

    // Even if HTTP status is not 200, we try to return the JSON body
    // since our backend always returns a valid structure
    return data;

  } catch (error) {
    if (error.name === 'AbortError') {
      return {
        results: [],
        error: 'request_timeout',
        query,
      };
    }

    return {
      results: [],
      error: 'connection_error',
      query,
    };
  } finally {
    clearTimeout(timeoutId);
  }
}
