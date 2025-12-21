const API_URL = import.meta.env.VITE_API_URL;

export async function predict(text) {
    const headers = { "Content-Type": "application/json" };
    const body = JSON.stringify({ text });

    try {
        const res = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers,
            body
        });

        if (!res.ok) {
            throw new Error("failed to fetch prediction results");
        }

        const prediction = await res.json();
        return prediction;

    } catch (error) {
        console.error(error.message);
        throw error;
    }
}

export async function highlight(text) {
    const headers = { "Content-Type": "application/json" };
    const body = JSON.stringify({ text });

    try {
        const res = await fetch(`${API_URL}/highlight`, {
            method: "POST",
            headers,
            body
        });

        if (!res.ok) {
            throw new Error("failed to fetch highlight results");
        }

        const highlight = await res.json();
        return highlight;

    } catch (error) {
        console.error(error.message);
        throw error;
    }
}
