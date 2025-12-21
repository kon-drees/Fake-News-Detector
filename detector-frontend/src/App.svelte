<script>
  import {predict, highlight} from './lib/api.js'

  let text = '';

  let loading = false;
  let error = '';

  let predictRes = null;
  let highlightRes = null;
  let predictionCategory = null;
  let score = null;


  async function analyze() {
    error = '';

    if (text.length < 10) {
      error = 'Please input a text of minimum ten characters.'
      return
    }

    predictRes = null;
    highlightRes = null;
    predictionCategory = null;
    score = null;

    loading = true;
    const predictPromise = predict(text);
    const highlightPromise = highlight(text);

    try {
      predictRes = await predictPromise;

      if (typeof predictRes?.prediction_result.score !== 'number') {
        throw new Error('Invalid prediction response');
      }

      score = predictRes.prediction_result.score.toFixed(4);

      if (score >= 0.9) {
        predictionCategory = 'Almost certainly fake news';
      } else if (score >= 0.7) {
        predictionCategory = 'Very likely fake news';
      } else if (score >= 0.5) {
        predictionCategory = 'Likely fake news';
      } else if (score >= 0.3) {
        predictionCategory = 'Likely not fake news';
      } else if (score >= 0.1) {
        predictionCategory = 'Very likely not fake news';
      } else {
        predictionCategory = 'Almost certainly not fake news';
      }
    } catch (err) {
      error = 'Prediction failed: ' + err.message;
    }

    try {
      highlightRes = await highlightPromise;
    } catch (err) {
      error += (error ? ' | ' : '') + 'Highlighting failed: ' + err.message;
    } finally {
      loading = false;
    }
  }



  function autoResize(element) {
    const el = element.target;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }

  // returns color gradient based on given value with green for postive and red for negative values
  function valueToBackground(value) {
    if (!value) return 'transparent';

    const intensity = Math.min(Math.abs(value), 1);

    if (value > 0) {
      // fake news contribution
      return `rgba(210, 0, 0, ${intensity})`;
    } else {
      // not fake news contribution
      return `rgba(0, 210, 0, ${intensity})`;
    }
  }


</script>

<main id="app-container">
  <section id="input-section">
    <h1 class="title">Fake News Detector</h1>
    <textarea id="text-input" class="input-box" on:input={autoResize} bind:value={text} placeholder="Paste a text or link here..."></textarea>
    <button id="analyze-button" class="btn" on:click={analyze} disabled={loading}>
      {loading ? "Analyzing..." : "Analyze"}
    </button>
    {#if error}
      <p class="error">{error}</p>
    {/if}
  </section>

  <hr class="divider"/>

  <section id="result-section">
    {#if predictRes !== null}
      <div id="prediction-values" class="result-card">
        <h2>Prediction Result</h2>
        <p><strong>Prediction:</strong> {predictionCategory}</p>
        <p><strong>Fake news probability score:</strong> {score * 100}%</p>
      </div>
    {/if}

    {#if highlightRes}
      <div id="highlighted-text" class="result-card">
        <h3>Prediction Reasoning</h3>

        <p class="highlight-legend">
          <span class="legend-green">Green</span> → Words contributing to a classification as not fake news.<br>
          <span class="legend-red">Red</span> → Words contributing to a classification as fake news.<br>
          The brightness represents how much influence the word had on the prediction result.
        </p>

        <hr class="divider" />

        <p class="highlighted-words">
          {#each highlightRes.highlights as token, i}
            <span class="highlight-word" style="background-color: {valueToBackground(token.score_normalized)}">
              {token.token}
            </span>
          {/each}
        </p>
      </div>
    {/if}
  </section>
</main>