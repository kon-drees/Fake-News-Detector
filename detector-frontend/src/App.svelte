<script>
  import {predictAndHighlight} from './lib/api.js'

  let text = '';

  let result = {
    predictionProbability: null,
    text: null,
    words: null,
    highlighting: null,
  }

  let loading = false;
  let error = '';

  let predictionResult = null;

  async function analyze() {
    loading = true;
    error = ''
    
    try {
      //result = await predictAndHighlight(text);
      // Dummy demonstration
      const dummytext = "BREAKING: Hidden technology has reportedly been discovered inside the newly released Covid 19 vaccines. Anonymous lab workers claim the vaccines contain micro-trackers, and several say they were pressured not to speak publicly. Independent investigators tried publishing their findings, but the reports allegedly vanished within hours. For the full documents, join our private channel before they disappear again.";
      result = {
        predictionProbability: 28.63,
        text: dummytext,
        words: dummytext.split(" "),
        highlighting: [0.5, 0.1, 0, 0.23, 0.22, -0.6, 1, -0.16, -1, -0.5, 0.1, 0, 0.23, 0.22, 0.6, 0.9, -0.16, -0.5, 0.1, 0, 0.23, 0.22, 0.6, 0.75, -0.36, -0.5, 0.1, 0, 0.23, 0.22, 0.6, 0.4, -0.16, 0.32, -0.6, 0.7, -0.16, -0.5, 0.1, 0.5, 0.23, 0.22, 0.6, 1, 0.16, -0.5, 0.1, 0, 0, -0.05, 0.43, 0.4, -0.6, 0.7, -0.1, 1, 0.2],
      }
    } catch (err) {
      error = 'Error while trying to predict and highlight: ' + err.message;
    } finally {
      loading = false;

      if (result.predictionProbability >= 90) {
          predictionResult = 'Almost certainly not fake news';
      } else if (result.predictionProbability >= 70) {
          predictionResult = 'Very likely not fake news';
      } else if (result.predictionProbability >= 50) {
          predictionResult = 'Likely not fake news';
      } else if (result.predictionProbability >= 30) {
          predictionResult = 'Likely fake news';
      } else if (result.predictionProbability >= 10){
          predictionResult = 'Very likely fake news'
      }
      else {
          predictionResult = 'Almost certainly fake news';
      }
    }
  }

  function autoResize(element) {
    const el = element.target;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }

  // returns color gradient based on given value with green for postive and red for negative values
  function valueToBackground(value) {
    if (value === 0) return 'transparent';
    if (value < 0) {
      // green for positive values
      return `rgba(0, 210, 0, ${-value})`; 
    } else {
      // red for negative values
      return `rgba(210, 0, 0, ${value})`;
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
    {#if result.predictionProbability !== null}
      <div id="prediction-values" class="result-card">
        <h2>Prediction Result</h2>
        <p><strong>Prediction:</strong> {predictionResult}</p>
        <p><strong>Fake news probability score:</strong> {100 - result.predictionProbability}%</p>
      </div>
    {/if}

    {#if result.words}
      <div id="highlighted-text" class="result-card">
        <h3>Prediction Reasoning</h3>
        <p class="highlight-legend">
          <span class="legend-green">Green</span> → Words contributing to a classification as not fake news.<br>
          <span class="legend-red">Red</span> → Words contributing to a classification as fake news.<br>
          The brightness represents how much influence the word had on the prediction result.
        </p>
        <hr class="divider"/>
        <p class="highlighted-words">
          {#each result.words as word, i}
            <span class="highlight-word" style="background-color: {valueToBackground(result.highlighting[i] || 0)}">
              {word}
            </span>{' '}
          {/each}
        </p>
      </div>
    {/if}
  </section>
</main>