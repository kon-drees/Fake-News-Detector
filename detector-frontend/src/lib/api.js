const API_URL = import.meta.env.VITE_API_URL;


// API Post Request helper
async function postRequest(endpoint, text) {
  // Set header to JSON
  const headers = { "Content-Type": "application/json" };
  const body = JSON.stringify({ text });

  try {
    // Triggers fetch request
    const res = await fetch(`${API_URL}/${endpoint}`, {
      method: "POST",
      headers,
      body
    });

    // Throw error if non 200 status code response
    if (!res.ok) {
      throw new Error(`Failed to fetch ${endpoint}: ${res.status} ${res.statusText}`);
    }

    // Return response as json
    return await res.json();
  } catch (error) {
    console.error(error.message);
    throw error;
  }
}

// Export functions for different api routes
export const predict = (text) => postRequest('predict', text);
export const highlight = (text) => postRequest('highlight', text);
export const factCheck = (text) => postRequest('fact-check', text);