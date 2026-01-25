const API_URL = import.meta.env.VITE_API_URL;


// API Post Request helper
async function postRequest(endpoint, text) {
  const headers = { "Content-Type": "application/json" };
  const body = JSON.stringify({ text });

  try {
    const res = await fetch(`${API_URL}/${endpoint}`, {
      method: "POST",
      headers,
      body
    });

    if (!res.ok) {
      throw new Error(`Failed to fetch ${endpoint}: ${res.status} ${res.statusText}`);
    }

    return await res.json();
  } catch (error) {
    console.error(error.message);
    throw error;
  }
}

export const predict = (text) => postRequest('predict', text);
export const highlight = (text) => postRequest('highlight', text);
export const factCheck = (text) => postRequest('fact-check', text);