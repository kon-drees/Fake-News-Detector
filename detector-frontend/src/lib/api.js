export async function predictAndHighlight(text) {
    const headers = {"Content-Type": "application/json"}
    const body = JSON.stringify({text})
    
    //GGfs API Url aus Env lesen
    try {
            const [predictRes, highlightRes] = await Promise.all([
        fetch("/predict", { method: "POST", headers, body }),
        fetch("/highlight", { method: "POST", headers, body })
        ]);

        if (!predictRes.ok && !highlightRes.ok) {
            throw new Error("failed to fetch both prediction and highlighting results");
        }
        else if (!predictRes.ok) {
            throw new Error("failed to fetch prediction results.");
        }
        else if (!highlightRes.ok) {
            throw new Error("failed to fetch highlighting results.");
        }

        const [prediction, highlight] = await Promise.all([
            predictRes.json(),
            highlightRes.json()
        ]);

        return {prediction, highlight}
        
    } catch (error) {
            console.error(error.message)
            throw error
    }    
}